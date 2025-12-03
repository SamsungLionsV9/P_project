import React, { useState, useEffect } from "react";

function DashboardPage() {
  const [stats, setStats] = useState({
    todayCount: 0,
    totalCount: 0,
    avgConfidence: 85,
    popularModels: [],
  });
  const [dailyData, setDailyData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        const statsRes = await fetch(
          "http://localhost:8001/api/admin/dashboard-stats"
        );
        const statsData = await statsRes.json();
        if (statsData.success) {
          setStats({
            todayCount: statsData.todayCount || 0,
            totalCount: statsData.totalCount || 0,
            avgConfidence: statsData.avgConfidence || 85,
            popularModels: statsData.popularModels || [],
          });
        }

        const dailyRes = await fetch(
          "http://localhost:8001/api/admin/daily-requests?days=7"
        );
        const dailyResult = await dailyRes.json();
        if (dailyResult.success) {
          setDailyData(dailyResult.data || []);
        }
      } catch (error) {
        console.error("Dashboard data load failed:", error);
      } finally {
        setLoading(false);
      }
    };

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

  return (
    <>
      {/* 카드 3개 */}
      <section className="stat-cards">
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-green">👁️</div>
            <span className="stat-label">오늘 시세 조회</span>
          </div>
          <div className="stat-value">{stats.todayCount.toLocaleString()}건</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-yellow">📁</div>
            <span className="stat-label">전체 누적 조회</span>
          </div>
          <div className="stat-value">{stats.totalCount.toLocaleString()}건</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-blue">✔️</div>
            <span className="stat-label">평균 신뢰도</span>
          </div>
          <div className="stat-value">{stats.avgConfidence}%</div>
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
                    style={{
                      height: `${(m.value / maxModelValue) * 100}%`,
                    }}
                  />
                  <span className="bar-label">{m.name || "기타"}</span>
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

