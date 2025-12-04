import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Eye, FolderOpen, CheckCircle, RefreshCw, AlertTriangle, TrendingUp, Clock, DollarSign, Fuel, Percent, ArrowUp, ArrowDown, Minus } from "lucide-react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

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
      {/* 통계 카드 3개 - Framer Motion 애니메이션 적용 */}
      <section className="stat-cards">
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
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
        </motion.div>

        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
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
        </motion.div>

        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }}
        >
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-blue"><CheckCircle size={20} /></div>
            <span className="stat-label">평균 신뢰도</span>
          </div>
          <div className="stat-value">
            {stats.avgConfidence > 0 ? `${stats.avgConfidence}%` : "-"}
          </div>
        </motion.div>
      </section>

      {/* 차트 1: 인기 많은 모델 조회수 (Recharts) */}
      <section className="chart-section">
        <h2 className="chart-title">인기 많은 모델 조회수</h2>
        <div className="chart-card" style={{ padding: '24px' }}>
          {stats.popularModels.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              아직 조회 데이터가 없습니다
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart 
                data={stats.popularModels} 
                margin={{ top: 30, right: 30, left: 20, bottom: 20 }}
                barCategoryGap="20%"
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 11, fill: '#555' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e0e0e0' }}
                  interval={0}
                />
                <YAxis 
                  tick={{ fontSize: 11, fill: '#666' }} 
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip 
                  contentStyle={{ 
                    background: 'white', 
                    border: 'none', 
                    borderRadius: '12px', 
                    boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                    padding: '12px 16px'
                  }}
                  formatter={(value) => [`${value}건`, '조회수']}
                  cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={60}>
                  {stats.popularModels.map((entry, index) => (
                    <Cell key={index} fill={`hsl(${240 - index * 25}, 70%, 55%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>

      {/* 차트 2: 일별 시세 분석 요청 수 (Recharts) */}
      <section className="chart-section">
        <h2 className="chart-title">일별 시세 분석 요청 수</h2>
        <div className="chart-card" style={{ padding: '20px' }}>
          {dailyData.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              최근 7일간 조회 데이터가 없습니다
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={dailyData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#666' }} />
                <YAxis tick={{ fontSize: 11, fill: '#666' }} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'white', 
                    border: 'none', 
                    borderRadius: '12px', 
                    boxShadow: '0 10px 25px rgba(0,0,0,0.1)' 
                  }}
                  formatter={(value) => [`${value}건`, '분석 요청']}
                />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorCount)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>
    </>
  );
}

export default DashboardPage;

