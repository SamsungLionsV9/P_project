import React, { useState, useEffect } from "react";
import Pagination from "../components/Pagination";

function HistoryPage() {
  const [userIdFilter, setUserIdFilter] = useState("");
  const [modelFilter, setModelFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [historyData, setHistoryData] = useState([]);
  const [displayedHistory, setDisplayedHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/admin/analysis-history?limit=100");
      if (!response.ok) {
        throw new Error(`서버 오류: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setHistoryData(data.history);
        setDisplayedHistory(data.history);
      } else {
        throw new Error(data.message || "데이터 로드 실패");
      }
    } catch (err) {
      console.error("Failed to load history:", err);
      setError(err.message || "분석 이력을 불러오는데 실패했습니다");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleSearch = () => {
    const filtered = historyData.filter((row) => {
      const matchUser =
        userIdFilter.trim() === "" ||
        (row.user_id &&
          row.user_id.toLowerCase().includes(userIdFilter.toLowerCase()));
      const matchModel =
        modelFilter.trim() === "" ||
        (row.model &&
          row.model.toLowerCase().includes(modelFilter.toLowerCase()));
      const matchDate =
        dateFilter.trim() === "" ||
        (row.searched_at && row.searched_at.includes(dateFilter.trim()));

      return matchUser && matchModel && matchDate;
    });
    setDisplayedHistory(filtered);
  };

  const handleReset = () => {
    setUserIdFilter("");
    setModelFilter("");
    setDateFilter("");
    setDisplayedHistory(historyData);
  };

  const formatPrice = (price) => {
    if (!price) return "-";
    return `${Math.round(price).toLocaleString()}만원`;
  };

  const formatMileage = (mileage) => {
    if (!mileage) return "-";
    return `${(mileage / 10000).toFixed(1)}만km`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    return dateStr.replace("T", " ").slice(0, 16);
  };

  return (
    <div className="page">
      <section className="content-header">
        <h2>분석 이력</h2>
      </section>

      <section className="filter-section">
        <div className="filter-card">
          <div className="filter-grid three">
            <div className="filter-field">
              <label>유저 아이디</label>
              <input
                placeholder="유저 ID 검색"
                value={userIdFilter}
                onChange={(e) => setUserIdFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>모델</label>
              <input
                placeholder="모델명 검색"
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>조회 일시</label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              />
            </div>
          </div>

          <div className="filter-actions">
            <button className="btn-primary" onClick={handleSearch}>
              검색
            </button>
            <button className="btn-ghost" onClick={handleReset}>
              초기화
            </button>
            <button className="btn-ghost" onClick={loadHistory}>
              새로고침
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">
            분석 이력 ({displayedHistory.length}건)
          </div>
        </div>

        <div className="table-card">
          {loading ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              로딩 중...
            </div>
          ) : error ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#e74c3c" }}>
              <div style={{ marginBottom: "10px" }}>⚠️ {error}</div>
              <button className="btn-primary" onClick={loadHistory}>
                다시 시도
              </button>
            </div>
          ) : displayedHistory.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              분석 이력이 없습니다. 사용자가 차량 가격 조회를 하면 이력이 쌓입니다.
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>조회 일시</th>
                  <th>유저 ID</th>
                  <th>브랜드</th>
                  <th>모델</th>
                  <th>연식</th>
                  <th>주행거리</th>
                  <th>연료</th>
                  <th>예상가</th>
                </tr>
              </thead>
              <tbody>
                {displayedHistory.map((row, i) => (
                  <tr key={row.id || i}>
                    <td>{formatDate(row.searched_at)}</td>
                    <td>{row.user_id || "-"}</td>
                    <td>{row.brand || "-"}</td>
                    <td>{row.model || "-"}</td>
                    <td>{row.year || "-"}</td>
                    <td>{formatMileage(row.mileage)}</td>
                    <td>{row.fuel || "-"}</td>
                    <td className="strong-text">
                      {formatPrice(row.predicted_price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <Pagination />
        </div>
      </section>
    </div>
  );
}

export default HistoryPage;

