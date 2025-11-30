import React, { useState, useEffect } from "react";
import { Eye, FolderOpen, CheckCircle, RefreshCw, AlertTriangle } from "lucide-react";

function DashboardPage() {
  const [stats, setStats] = useState({
    todayCount: 0,
    totalCount: 0,
    todayPredictions: 0,
    todayViews: 0,
    totalPredictions: 0,
    totalViews: 0,
    avgConfidence: 0,  // 실제 DB 값 사용 (더미 제거)
    popularModels: [],
    aiStats: {},
  });
  const [dailyData, setDailyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 확장된 통계 API 사용 (시세 예측 + 매물 조회 포함)
      const statsRes = await fetch("/api/admin/dashboard-stats-extended");
      if (!statsRes.ok) {
        throw new Error(`서버 오류: ${statsRes.status}`);
      }
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats({
          todayCount: statsData.todayTotal || statsData.todayCount || 0,
          totalCount: statsData.totalCount || 0,
          todayPredictions: statsData.todayPredictions || 0,
          todayViews: statsData.todayViews || 0,
          totalPredictions: statsData.totalPredictions || 0,
          totalViews: statsData.totalViews || 0,
          avgConfidence: statsData.avgConfidence || 0,  // 실제 DB 값만 사용
          popularModels: statsData.popularModels || [],
          aiStats: statsData.aiStats || {},
        });
      }

      const dailyRes = await fetch("/api/admin/daily-requests?days=7");
      const dailyResult = await dailyRes.json();
      if (dailyResult.success) {
        setDailyData(dailyResult.data || []);
      }
    } catch (err) {
      console.error("Dashboard data load failed:", err);
      setError(err.message || "대시보드 데이터를 불러오는데 실패했습니다");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const maxModelValue = Math.max(
    ...stats.popularModels.map((m) => m.value || 1),
    1
  );
  const dailyValues = dailyData.map((d) => d.count || 0);
  const dailyLabels = dailyData.map((d) => d.day || "");

  const getLinePoints = (values) => {
    if (!values.length) return "0,100";
    const max = Math.max(...values, 1);
    const width = 100;
    const height = 100;
    return values
      .map((v, i) => {
        const x = values.length > 1 ? (i / (values.length - 1)) * width : 50;
        const y = height - (v / max) * height;
        return `${x},${y}`;
      })
      .join(" ");
  };

  if (loading) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
        대시보드 데이터 로딩 중...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#e74c3c" }}>
        <div style={{ marginBottom: "10px", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
          <AlertTriangle size={18} /> {error}
        </div>
        <button className="btn-primary" onClick={loadDashboardData} style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
          <RefreshCw size={14} /> 다시 시도
        </button>
      </div>
    );
  }

  return (
    <>
      {/* 통계 카드 3개 */}
      <section className="stat-cards">
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-green"><Eye size={20} /></div>
            <span className="stat-label">오늘 전체 조회</span>
          </div>
          <div className="stat-value">
            {stats.todayCount > 0 ? `${stats.todayCount.toLocaleString()}건` : "0건"}
          </div>
          <div className="stat-detail" style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
            시세예측 {stats.todayPredictions || 0}건 / 매물조회 {stats.todayViews || 0}건
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-yellow"><FolderOpen size={20} /></div>
            <span className="stat-label">전체 누적 조회</span>
          </div>
          <div className="stat-value">
            {stats.totalCount > 0 ? `${stats.totalCount.toLocaleString()}건` : "0건"}
          </div>
          <div className="stat-detail" style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
            예측 {stats.totalPredictions || 0} / 조회 {stats.totalViews || 0}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-blue"><CheckCircle size={20} /></div>
            <span className="stat-label">평균 신뢰도</span>
          </div>
          <div className="stat-value">
            {stats.avgConfidence > 0 ? `${stats.avgConfidence}%` : "-"}
          </div>
        </div>
      </section>

      {/* 차트 1: 인기 많은 모델 조회수 */}
      <section className="chart-section">
        <h2 className="chart-title">인기 많은 모델 조회수</h2>
        <div className="chart-card">
          {stats.popularModels.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              아직 조회 데이터가 없습니다
            </div>
          ) : (
            <div className="bar-chart">
              {stats.popularModels.map((m, idx) => (
                <div key={m.name || idx} className="bar-item">
                  <div
                    className="bar"
                    data-value={m.value || 0}
                    style={{
                      height: `${Math.max((m.value / maxModelValue) * 100, 5)}%`,
                    }}
                  />
                  <span className="bar-label" title={m.name || "기타"}>
                    {m.name || "기타"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* 차트 2: 일별 시세 분석 요청 수 */}
      <section className="chart-section">
        <h2 className="chart-title">일별 시세 분석 요청 수</h2>
        <div className="chart-card">
          {dailyValues.length === 0 || dailyValues.every((v) => v === 0) ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              최근 7일간 조회 데이터가 없습니다
            </div>
          ) : (
            <div className="line-chart-wrapper">
              <svg
                className="line-chart"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
              >
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2f57ff" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#2f57ff" stopOpacity="0" />
                  </linearGradient>
                </defs>

                <polygon
                  fill="url(#areaGradient)"
                  points={`0,100 ${getLinePoints(dailyValues)} 100,100`}
                />

                <polyline
                  fill="none"
                  stroke="#2f57ff"
                  strokeWidth="1.5"
                  points={getLinePoints(dailyValues)}
                />

                {dailyValues.map((v, i) => {
                  const max = Math.max(...dailyValues, 1);
                  const x =
                    dailyValues.length > 1 ? (i / (dailyValues.length - 1)) * 100 : 50;
                  const y = 100 - (v / max) * 100;
                  return <circle key={i} cx={x} cy={y} r="1.3" fill="#2f57ff" />;
                })}
              </svg>

              <div className="line-x-labels">
                {dailyLabels.map((l, i) => (
                  <span key={i}>{l}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}

export default DashboardPage;

