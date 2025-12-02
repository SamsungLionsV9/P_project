import React, { useState, useEffect } from "react";
import { Bot, RefreshCw, CheckCircle, XCircle, MessageSquare, AlertTriangle, Activity, ChevronDown, ChevronUp, TrendingUp, Shield, FileText } from "lucide-react";
import Pagination from "../components/Pagination";

function AILogPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState("");
  const [expandedLogId, setExpandedLogId] = useState(null);
  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const PAGE_SIZE = 20;

  const loadLogs = async (page = currentPage) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterType) params.append("log_type", filterType);
      params.append("page", String(page));
      params.append("limit", String(PAGE_SIZE));

      const response = await fetch(`/api/admin/ai-logs?${params}`);
      if (!response.ok) {
        throw new Error(`서버 오류: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setLogs(data.logs || []);
        setStats(data.stats || {});
        setTotalPages(data.totalPages || 1);
        setTotalCount(data.total || 0);
        setCurrentPage(data.page || 1);
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

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      loadLogs(page);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    loadLogs(1);
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
      case 'request': return reqData;
      case 'response': return resData;
      default: return log[field];
    }
  };

  // 상세 정보 렌더링
  const renderDetailSection = (log) => {
    const reqData = getLogField(log, 'request');
    const resData = getLogField(log, 'response');
    const logType = getLogField(log, 'type');

    return (
      <div className="log-detail-panel">
        {/* 요청 데이터 섹션 */}
        <div className="detail-section">
          <h4><FileText size={16} /> 요청 데이터</h4>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">차량</span>
              <span className="detail-value">{reqData.brand} {reqData.model} {reqData.year}년식</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">주행거리</span>
              <span className="detail-value">{reqData.mileage?.toLocaleString() || '-'}km</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">예측가</span>
              <span className="detail-value">{reqData.predicted_price?.toLocaleString() || '-'}만원</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">판매가</span>
              <span className="detail-value">{reqData.sale_price?.toLocaleString() || '-'}만원</span>
            </div>
          </div>
        </div>

        {/* 시그널 분석 결과 */}
        {(logType === 'signal' || resData.signal) && (
          <div className="detail-section signal-section">
            <h4><TrendingUp size={16} /> 시그널 분석 결과</h4>
            {resData.signal ? (
              <div className="signal-result">
                <div className={`signal-badge ${resData.signal.signal?.toLowerCase() || 'unknown'}`}>
                  {resData.signal.signal || '분석중'}
                </div>
                <p className="signal-summary">{resData.signal.summary || resData.signal.reason || '-'}</p>
                {resData.signal.price_gap && (
                  <div className="detail-item">
                    <span className="detail-label">가격 차이</span>
                    <span className="detail-value">{resData.signal.price_gap}만원 ({resData.signal.price_gap_percent || '-'}%)</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="no-data">시그널 분석 데이터 없음</p>
            )}
          </div>
        )}

        {/* 허위매물 탐지 결과 */}
        {(logType === 'fraud_detection' || resData.fraud_check) && (
          <div className="detail-section fraud-section">
            <h4><Shield size={16} /> 허위매물 탐지 결과</h4>
            {resData.fraud_check ? (
              <div className="fraud-result">
                <div className={`risk-badge ${resData.fraud_check.risk_level?.toLowerCase() || 'unknown'}`}>
                  위험도: {resData.fraud_check.risk_level || '알 수 없음'}
                </div>
                <div className="risk-score">
                  <span className="detail-label">위험 점수</span>
                  <span className="detail-value">{resData.fraud_check.risk_score || 0}/100</span>
                </div>
                {resData.fraud_check.warnings && resData.fraud_check.warnings.length > 0 && (
                  <div className="warnings-list">
                    <span className="detail-label">경고 사항</span>
                    <ul>
                      {resData.fraud_check.warnings.map((w, i) => (
                        <li key={i}><AlertTriangle size={12} /> {w}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {resData.fraud_check.summary && (
                  <p className="fraud-summary">{resData.fraud_check.summary}</p>
                )}
              </div>
            ) : (
              <p className="no-data">허위매물 탐지 데이터 없음</p>
            )}
          </div>
        )}

        {/* 네고 대본 결과 - 항상 표시 (negotiation 타입이거나 데이터가 있을 때) */}
        {(logType === 'negotiation' || resData.negotiation || resData.scripts || resData.script) && (
          <div className="detail-section negotiation-section">
            <h4><MessageSquare size={16} /> 네고 대본</h4>
            <div className="negotiation-result">
              {/* 문자 메시지 대본 */}
              {(resData.negotiation?.script || resData.script) && (
                <div className="script-item message-script">
                  <span className="script-label">📱 문자 메시지 대본</span>
                  <p className="script-text">{resData.negotiation?.script || resData.script}</p>
                </div>
              )}
              
              {/* 전화 대본 목록 */}
              {(resData.negotiation?.phone_scripts || resData.scripts || []).length > 0 && (
                <div className="scripts-list">
                  <span className="script-label" style={{marginBottom: '8px', display: 'block'}}>📞 전화 협상 대본</span>
                  {(resData.negotiation?.phone_scripts || resData.scripts || []).map((script, i) => (
                    <div key={i} className="script-item">
                      {typeof script === 'string' ? (
                        <p className="script-text">{script}</p>
                      ) : (
                        <>
                          <span className="script-label">{script.situation || `단계 ${i+1}`}</span>
                          <p className="script-text">{script.script || script.text || script}</p>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {/* 제안 가격 */}
              {(resData.negotiation?.target_price || resData.target_price) && (
                <div className="detail-item" style={{marginTop: '12px'}}>
                  <span className="detail-label">💰 제안 가격</span>
                  <span className="detail-value" style={{color: '#38a169', fontWeight: 'bold'}}>
                    {(resData.negotiation?.target_price || resData.target_price)?.toLocaleString()}만원
                  </span>
                </div>
              )}
              
              {/* 협상 팁 */}
              {(resData.negotiation?.tip || resData.tip) && (
                <div className="detail-item" style={{marginTop: '8px'}}>
                  <span className="detail-label">💡 협상 팁</span>
                  <span className="detail-value">{resData.negotiation?.tip || resData.tip}</span>
                </div>
              )}
              
              {/* 데이터가 전혀 없을 때 */}
              {!resData.negotiation?.script && !resData.script && 
               !(resData.negotiation?.phone_scripts || resData.scripts || []).length && (
                <p className="no-data">네고 대본 데이터가 아직 생성되지 않았습니다</p>
              )}
            </div>
          </div>
        )}

        {/* Raw 데이터 (디버깅용) */}
        <details className="raw-data-section">
          <summary>원본 데이터 (디버깅용)</summary>
          <pre>{JSON.stringify({ request: reqData, response: resData }, null, 2)}</pre>
        </details>
      </div>
    );
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

      {/* 통계 카드 - 대시보드 스타일 통일 */}
      <section className="stat-cards" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-blue"><Bot size={20} /></div>
            <span className="stat-label">총 AI 호출</span>
          </div>
          <div className="stat-value">{stats.total_calls || 0}건</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-green"><FileText size={20} /></div>
            <span className="stat-label">네고 대본 생성</span>
          </div>
          <div className="stat-value">{stats.negotiation_scripts || 0}건</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-yellow"><TrendingUp size={20} /></div>
            <span className="stat-label">시그널 분석</span>
          </div>
          <div className="stat-value">{stats.signal_reports || 0}건</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-red"><Shield size={20} /></div>
            <span className="stat-label">허위매물 탐지</span>
          </div>
          <div className="stat-value">{stats.fraud_detections || 0}건</div>
        </div>
      </section>

      {/* 필터 - 가로 배열 */}
      <section style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{ 
              padding: '10px 16px', 
              borderRadius: '8px', 
              border: '1px solid #ddd',
              fontSize: '14px',
              minWidth: '120px'
            }}
          >
            <option value="">전체 유형</option>
            <option value="negotiation">네고 대본</option>
            <option value="signal">시그널 분석</option>
            <option value="fraud_detection">허위매물 탐지</option>
          </select>
          <span style={{ color: '#666', fontSize: '14px' }}>
            총 {totalCount.toLocaleString()}건
          </span>
          <button 
            onClick={() => loadLogs(currentPage)} 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
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
                  <th>상세</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => {
                  const logType = getLogField(log, 'type');
                  const isSuccess = getLogField(log, 'success');
                  const logId = log.id || i;
                  const isExpanded = expandedLogId === logId;
                  return (
                    <React.Fragment key={logId}>
                      <tr 
                        className={`clickable-row ${isExpanded ? 'expanded' : ''}`}
                        onClick={() => setExpandedLogId(isExpanded ? null : logId)}
                      >
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
                        <td>
                          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="detail-row">
                          <td colSpan="8">
                            {renderDetailSection(log)}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
        {!loading && logs.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        )}
      </section>
    </div>
  );
}

export default AILogPage;

