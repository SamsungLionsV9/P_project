import React, { useState, useEffect } from "react";
import { Bot, RefreshCw, CheckCircle, XCircle, MessageSquare, AlertTriangle, Activity } from "lucide-react";

function AILogPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState("");

  const loadLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterType) params.append("log_type", filterType);
      params.append("limit", "50");

      const response = await fetch(`/api/admin/ai-logs?${params}`);
      if (!response.ok) {
        throw new Error(`서버 오류: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setLogs(data.logs || []);
        setStats(data.stats || {});
      } else {
        throw new Error(data.message || "데이터 로드 실패");
      }
    } catch (err) {
      console.error("Failed to load AI logs:", err);
      setError(err.message || "AI 로그를 불러오는데 실패했습니다");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [filterType]);

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    try {
      // "2025-11-29 11:10:54" 형식 처리
      const date = new Date(dateString.replace(' ', 'T'));
      return date.toLocaleString("ko-KR");
    } catch {
      return dateString;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case "negotiation": return "네고 대본";
      case "signal": return "시그널 분석";
      case "fraud_detection": return "허위매물 탐지";
      default: return type || "-";
    }
  };

  // API 응답에서 필드 추출 (필드명 호환성 처리)
  const getLogField = (log, field) => {
    // request_data 또는 request에서 가져오기
    const reqData = log.request_data || log.request || {};
    // response_data 또는 response에서 가져오기
    const resData = log.response_data || log.response || {};

    switch(field) {
      case 'timestamp': return log.created_at || log.timestamp;
      case 'type': return log.log_type || log.type;
      case 'brand': return reqData.brand;
      case 'model': return reqData.model;
      case 'predicted_price': return reqData.predicted_price;
      case 'sale_price': return reqData.sale_price;
      case 'success': return resData.success;
      default: return log[field];
    }
  };

  return (
    <div className="page-container">
      <header className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Bot size={28} />
          <h1 style={{ margin: 0 }}>AI 분석 로그</h1>
        </div>
        <p>Groq AI를 통한 네고 대본 생성 및 분석 기록</p>
      </header>

      {/* 통계 카드 */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_calls || 0}</div>
          <div className="stat-label">총 AI 호출</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.negotiation_scripts || 0}</div>
          <div className="stat-label">네고 대본 생성</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.signal_reports || 0}</div>
          <div className="stat-label">시그널 분석</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.fraud_detections || 0}</div>
          <div className="stat-label">허위매물 탐지</div>
        </div>
      </section>

      {/* 필터 */}
      <section className="filter-section">
        <div className="filter-row">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="">전체 유형</option>
            <option value="negotiation">네고 대본</option>
            <option value="signal">시그널 분석</option>
            <option value="fraud_detection">허위매물 탐지</option>
          </select>
          <button className="btn-primary" onClick={loadLogs} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <RefreshCw size={16} />
            새로고침
          </button>
        </div>
      </section>

      {/* 로그 테이블 */}
      <section className="table-section">
        <div className="table-container">
          {loading ? (
            <p className="loading-text">로딩 중...</p>
          ) : error ? (
            <p className="error-text">{error}</p>
          ) : logs.length === 0 ? (
            <p className="empty-text">AI 로그가 없습니다</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>시간</th>
                  <th>유형</th>
                  <th>차량</th>
                  <th>예측가</th>
                  <th>판매가</th>
                  <th>AI 모델</th>
                  <th>결과</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => {
                  const logType = getLogField(log, 'type');
                  const isSuccess = getLogField(log, 'success');
                  return (
                    <tr key={log.id || i}>
                      <td>{formatDate(getLogField(log, 'timestamp'))}</td>
                      <td>
                        <span className={`type-badge ${logType}`}>
                          {getTypeLabel(logType)}
                        </span>
                      </td>
                      <td>{getLogField(log, 'brand')} {getLogField(log, 'model')}</td>
                      <td>{getLogField(log, 'predicted_price')?.toLocaleString() || "-"}만원</td>
                      <td>{getLogField(log, 'sale_price')?.toLocaleString() || "-"}만원</td>
                      <td>{log.ai_model || "-"}</td>
                      <td>
                        <span className={isSuccess ? "text-success" : "text-error"} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          {isSuccess ? <><CheckCircle size={14} /> 성공</> : <><XCircle size={14} /> 실패</>}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}

export default AILogPage;

