import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Calendar,
  DollarSign,
  Fuel,
  Building2,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  Target,
  LineChart,
  Rocket,
  MapPin,
  ArrowRight,
} from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_BASE = "";  // 프록시 사용 (vite.config.js)

/**
 * 경제지표 인사이트 페이지 (Phase 3 고도화)
 * - T3.1: 전월 대비 추세
 * - T3.3: 지역별 수요
 * - T3.4: 향후 1-2주 예측
 */
function EconomicInsightsPage() {
  const [insights, setInsights] = useState(null);
  const [marketTiming, setMarketTiming] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Phase 3: 고도화된 경제 인사이트 로드
  const fetchInsights = async () => {
    setLoading(true);
    try {
      // 새로운 API 호출
      const [insightsRes, timingRes] = await Promise.all([
        fetch(`${API_BASE}/api/economic-insights`),
        fetch(`${API_BASE}/api/market-timing`)
      ]);
      
      const insightsData = await insightsRes.json();
      const timingData = await timingRes.json();
      
      setInsights(insightsData);
      setMarketTiming(timingData);
      setLastUpdate(new Date());
      setError(null);
    } catch (e) {
      setError("경제 인사이트 데이터를 불러올 수 없습니다");
      console.error("Economic insights fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
    // 5분마다 자동 갱신
    const interval = setInterval(fetchInsights, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // 점수에 따른 색상
  const getScoreColor = (score) => {
    if (score >= 70) return "#22c55e";
    if (score >= 55) return "#3b82f6";
    if (score >= 45) return "#f59e0b";
    return "#ef4444";
  };

  // 상태에 따른 아이콘
  const getStatusIcon = (status) => {
    switch (status) {
      case "positive":
        return <TrendingUp size={16} color="#22c55e" />;
      case "negative":
        return <TrendingDown size={16} color="#ef4444" />;
      default:
        return <Minus size={16} color="#6b7280" />;
    }
  };

  // 지표 아이콘
  const getIndicatorIcon = (name) => {
    if (name.includes("금리")) return <Building2 size={20} />;
    if (name.includes("유가")) return <Fuel size={20} />;
    if (name.includes("환율")) return <DollarSign size={20} />;
    if (name.includes("신차")) return <Calendar size={20} />;
    return <TrendingUp size={20} />;
  };

  if (loading && !marketTiming) {
    return (
      <div className="page-content">
        <div className="loading-state">
          <RefreshCw className="spin" size={32} />
          <p>경제지표 분석 중...</p>
        </div>
      </div>
    );
  }

  const scoreColor = marketTiming ? getScoreColor(marketTiming.score) : "#6b7280";

  return (
    <div className="page-content">
      {/* 페이지 헤더 */}
      <div className="page-header-row">
        <div>
          <h2>경제지표 인사이트</h2>
          <p className="page-desc">
            ★ 차별화 포인트: 경제지표 기반 구매 타이밍 분석 (경쟁사에 없는 기능)
          </p>
        </div>
        <button className="refresh-btn" onClick={fetchInsights} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          새로고침
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* 메인 타이밍 점수 카드 */}
      <div className="insights-grid">
        <div
          className="timing-score-card"
          style={{
            background: `linear-gradient(135deg, ${scoreColor}20 0%, ${scoreColor}05 100%)`,
            borderColor: `${scoreColor}40`,
          }}
        >
          <div className="timing-header">
            <Clock size={20} color={scoreColor} />
            <span>오늘의 구매 타이밍</span>
            <span
              className="timing-label"
              style={{ background: `${scoreColor}20`, color: scoreColor }}
            >
              {marketTiming?.label || "분석 중"}
            </span>
          </div>

          <div className="timing-score-display">
            <span className="score-number" style={{ color: scoreColor }}>
              {marketTiming?.score?.toFixed(0) || "--"}
            </span>
            <span className="score-suffix">/ 100</span>
          </div>

          <div className="timing-action" style={{ color: scoreColor }}>
            {marketTiming?.action || "데이터 수집 중"}
          </div>

          <div className="timing-message">
            {marketTiming?.message || "시장 데이터를 분석하고 있습니다"}
          </div>

          {lastUpdate && (
            <div className="update-time">
              마지막 업데이트: {lastUpdate.toLocaleString("ko-KR")}
            </div>
          )}
        </div>

        {/* 경제지표 카드 */}
        <div className="indicators-card">
          <h3>
            <TrendingUp size={18} />
            경제지표 현황
          </h3>
          <div className="indicators-list">
            {marketTiming?.indicators?.map((indicator, idx) => (
              <div key={idx} className="indicator-item">
                <div className="indicator-icon">{getIndicatorIcon(indicator.name)}</div>
                <div className="indicator-info">
                  <span className="indicator-name">{indicator.name}</span>
                  <span className="indicator-desc">{indicator.desc}</span>
                </div>
                <div className="indicator-status">{getStatusIcon(indicator.status)}</div>
              </div>
            )) || (
              <div className="empty-state">지표 데이터 없음</div>
            )}
          </div>
        </div>
      </div>

      {/* 분석 인사이트 */}
      <div className="insights-section">
        <h3>
          <CheckCircle size={18} />
          타이밍 분석 인사이트
        </h3>
        <div className="reasons-list">
          {marketTiming?.reasons?.length > 0 ? (
            marketTiming.reasons.map((reason, idx) => (
              <div key={idx} className="reason-item">
                <span className="reason-bullet">•</span>
                <span>{reason.replace(/[✅❌🟢🟡🔴⚠️]/g, "").trim()}</span>
              </div>
            ))
          ) : (
            <div className="empty-state">분석 데이터가 없습니다</div>
          )}
        </div>
      </div>

      {/* T3.1: 경제지표 전월 대비 추세 */}
      {insights?.economic_indicators && (
        <div className="insights-section">
          <h3>
            <TrendingUp size={18} />
            경제지표 전월 대비 추세
            <span className="phase-badge">Phase 3</span>
          </h3>
          <div className="indicators-trend-grid">
            {/* 유가 */}
            <div className="trend-card">
              <div className="trend-header">
                <Fuel size={20} color="#3b82f6" />
                <span>국제유가 (WTI)</span>
              </div>
              <div className="trend-value">${insights.economic_indicators.oil?.current || '--'}</div>
              <div className={`trend-change ${insights.economic_indicators.oil?.trend === 'down' ? 'positive' : insights.economic_indicators.oil?.trend === 'up' ? 'negative' : ''}`}>
                {insights.economic_indicators.oil?.trend === 'down' ? <TrendingDown size={14} /> : insights.economic_indicators.oil?.trend === 'up' ? <TrendingUp size={14} /> : <Minus size={14} />}
                {insights.economic_indicators.oil?.change_pct?.toFixed(1) || 0}% (전월 대비)
              </div>
              <div className="trend-signal">신호: {insights.economic_indicators.oil?.signal || 'hold'}</div>
            </div>
            
            {/* 환율 */}
            <div className="trend-card">
              <div className="trend-header">
                <DollarSign size={20} color="#f59e0b" />
                <span>환율 (USD/KRW)</span>
              </div>
              <div className="trend-value">₩{insights.economic_indicators.exchange?.current?.toLocaleString() || '--'}</div>
              <div className={`trend-change ${insights.economic_indicators.exchange?.trend === 'down' ? 'positive' : insights.economic_indicators.exchange?.trend === 'up' ? 'negative' : ''}`}>
                {insights.economic_indicators.exchange?.trend === 'down' ? <TrendingDown size={14} /> : insights.economic_indicators.exchange?.trend === 'up' ? <TrendingUp size={14} /> : <Minus size={14} />}
                {insights.economic_indicators.exchange?.change_pct?.toFixed(1) || 0}% (전월 대비)
              </div>
              <div className="trend-signal">신호: {insights.economic_indicators.exchange?.signal || 'hold'}</div>
            </div>
            
            {/* 금리 */}
            <div className="trend-card">
              <div className="trend-header">
                <Building2 size={20} color="#22c55e" />
                <span>기준금리</span>
              </div>
              <div className="trend-value">{insights.economic_indicators.interest?.current || '--'}%</div>
              <div className="trend-change neutral">
                <Calendar size={14} />
                다음 금통위: {insights.economic_indicators.interest?.days_until || '--'}일 후
              </div>
              <div className="trend-signal">신호: {insights.economic_indicators.interest?.signal || 'hold'}</div>
            </div>
          </div>
        </div>
      )}

      {/* T3.4: 향후 1-2주 타이밍 예측 */}
      {insights?.prediction?.chart_data && (
        <div className="insights-section">
          <h3>
            <LineChart size={18} />
            향후 2주 타이밍 예측
            <span className="phase-badge">Phase 3</span>
          </h3>
          <div className="prediction-content">
            <div className="prediction-chart">
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={insights.prediction.chart_data}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#666' }} />
                  <YAxis domain={[30, 85]} tick={{ fontSize: 11, fill: '#666' }} />
                  <Tooltip 
                    contentStyle={{ background: 'white', border: 'none', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                    formatter={(value) => [`${value}점`, '타이밍 점수']}
                  />
                  <Area type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={2} fill="url(#colorScore)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="prediction-summary">
              <div className="summary-item">
                <span className="summary-label">이번 주 평균</span>
                <span className="summary-value">{insights.prediction.this_week?.avg_score || '--'}점</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">다음 주 평균</span>
                <span className="summary-value">{insights.prediction.next_week?.avg_score || '--'}점</span>
              </div>
              <div className="summary-item best">
                <span className="summary-label">최적 구매일</span>
                <span className="summary-value">{insights.prediction.this_week?.best_day?.slice(-5) || '--'}</span>
              </div>
              <div className="recommendation-box">
                <ArrowRight size={16} />
                {insights.prediction.recommendation || '분석 중...'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* T3.3: 지역별 수요 현황 */}
      {insights?.regional && (
        <div className="insights-section">
          <h3>
            <MapPin size={18} />
            지역별 수요 현황
            <span className="phase-badge">Phase 3</span>
          </h3>
          <div className="regional-info">
            <div className="regional-current">
              <div className="regional-label">현재 분석 지역</div>
              <div className="regional-value">{insights.regional.region || '전국'}</div>
              <div className="regional-demand">수요 지수: {insights.regional.demand_index || 50}</div>
              <div className="regional-recommendation">{insights.regional.recommendation || ''}</div>
            </div>
            {insights.regional.nearby_alternatives?.length > 0 && (
              <div className="nearby-regions">
                <div className="nearby-title">구매 추천 지역 (낮은 수요)</div>
                {insights.regional.nearby_alternatives.map((r, idx) => (
                  <div key={idx} className="nearby-item">
                    <MapPin size={14} />
                    <span>{r.region}</span>
                    <span className="nearby-demand">수요 {r.demand_index}</span>
                    <span className="nearby-premium">{r.price_premium > 0 ? '+' : ''}{r.price_premium}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* B2B 확장 정보 */}
      <div className="b2b-info-card">
        <h3>
          <Rocket size={18} />
          B2B 데이터 서비스 확장 계획
        </h3>
        <div className="b2b-features">
          <div className="b2b-feature">
            <div className="feature-icon-box">
              <BarChart3 size={24} color="#3b82f6" />
            </div>
            <div>
              <strong>시장 인텔리전스 API</strong>
              <p>딜러/매매상에 경제지표 기반 시장 동향 데이터 제공</p>
            </div>
          </div>
          <div className="b2b-feature">
            <div className="feature-icon-box">
              <Target size={24} color="#22c55e" />
            </div>
            <div>
              <strong>판매 타이밍 추천</strong>
              <p>판매자를 위한 최적 판매 시기 분석</p>
            </div>
          </div>
          <div className="b2b-feature">
            <div className="feature-icon-box">
              <LineChart size={24} color="#f59e0b" />
            </div>
            <div>
              <strong>가격 트렌드 리포트</strong>
              <p>모델별/지역별 시세 변동 예측 리포트</p>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .page-header-row {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }
        .page-header-row h2 {
          margin: 0 0 4px 0;
          font-size: 20px;
        }
        .page-desc {
          color: #6b7280;
          font-size: 13px;
          margin: 0;
        }
        .refresh-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          font-size: 13px;
        }
        .refresh-btn:hover {
          background: #e5e7eb;
        }
        .refresh-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .error-banner {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #dc2626;
          margin-bottom: 20px;
        }
        .insights-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 20px;
        }
        .timing-score-card {
          padding: 24px;
          border-radius: 16px;
          border: 2px solid;
        }
        .timing-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 16px;
        }
        .timing-label {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          margin-left: auto;
        }
        .timing-score-display {
          display: flex;
          align-items: baseline;
          justify-content: center;
          margin-bottom: 12px;
        }
        .score-number {
          font-size: 72px;
          font-weight: 700;
          line-height: 1;
        }
        .score-suffix {
          font-size: 20px;
          color: #9ca3af;
          margin-left: 4px;
        }
        .timing-action {
          text-align: center;
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
        }
        .timing-message {
          text-align: center;
          font-size: 13px;
          color: #6b7280;
        }
        .update-time {
          text-align: center;
          font-size: 11px;
          color: #9ca3af;
          margin-top: 16px;
        }
        .indicators-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          border: 1px solid #e5e7eb;
        }
        .indicators-card h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          margin: 0 0 16px 0;
        }
        .indicators-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .indicator-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #f9fafb;
          border-radius: 10px;
        }
        .indicator-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 10px;
          color: #6b7280;
        }
        .indicator-info {
          flex: 1;
        }
        .indicator-name {
          display: block;
          font-weight: 600;
          font-size: 14px;
        }
        .indicator-desc {
          font-size: 12px;
          color: #6b7280;
        }
        .insights-section {
          background: white;
          border-radius: 16px;
          padding: 20px;
          border: 1px solid #e5e7eb;
          margin-bottom: 20px;
        }
        .insights-section h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          margin: 0 0 16px 0;
        }
        .phase-badge {
          background: linear-gradient(135deg, #8b5cf6, #6366f1);
          color: white;
          font-size: 10px;
          padding: 3px 8px;
          border-radius: 10px;
          margin-left: auto;
          font-weight: 600;
        }
        .indicators-trend-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }
        .trend-card {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
        }
        .trend-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #6b7280;
          margin-bottom: 8px;
        }
        .trend-value {
          font-size: 28px;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 8px;
        }
        .trend-change {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #6b7280;
        }
        .trend-change.positive { color: #22c55e; }
        .trend-change.negative { color: #ef4444; }
        .trend-change.neutral { color: #6b7280; }
        .trend-signal {
          font-size: 11px;
          color: #9ca3af;
          margin-top: 8px;
        }
        .prediction-content {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 20px;
        }
        .prediction-chart {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
        }
        .prediction-summary {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .summary-item {
          display: flex;
          justify-content: space-between;
          padding: 12px;
          background: #f9fafb;
          border-radius: 8px;
        }
        .summary-item.best {
          background: linear-gradient(135deg, #ecfdf5, #d1fae5);
          border: 1px solid #6ee7b7;
        }
        .summary-label {
          font-size: 12px;
          color: #6b7280;
        }
        .summary-value {
          font-size: 14px;
          font-weight: 600;
          color: #1f2937;
        }
        .recommendation-box {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: linear-gradient(135deg, #eff6ff, #dbeafe);
          border-radius: 8px;
          font-size: 13px;
          color: #1d4ed8;
        }
        .regional-info {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }
        .regional-current {
          background: #f9fafb;
          border-radius: 12px;
          padding: 20px;
        }
        .regional-label {
          font-size: 12px;
          color: #6b7280;
          margin-bottom: 4px;
        }
        .regional-value {
          font-size: 24px;
          font-weight: 700;
          color: #1f2937;
        }
        .regional-demand {
          font-size: 14px;
          color: #3b82f6;
          margin: 8px 0;
        }
        .regional-recommendation {
          font-size: 12px;
          color: #6b7280;
        }
        .nearby-regions {
          background: #f9fafb;
          border-radius: 12px;
          padding: 16px;
        }
        .nearby-title {
          font-size: 13px;
          font-weight: 600;
          margin-bottom: 12px;
        }
        .nearby-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          border-bottom: 1px solid #e5e7eb;
          font-size: 13px;
        }
        .nearby-item:last-child { border-bottom: none; }
        .nearby-demand {
          margin-left: auto;
          color: #6b7280;
        }
        .nearby-premium {
          color: #22c55e;
          font-weight: 500;
        }
        .reasons-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .reason-item {
          display: flex;
          gap: 8px;
          font-size: 14px;
          color: #374151;
        }
        .reason-bullet {
          color: #3b82f6;
        }
        .empty-state {
          color: #9ca3af;
          font-size: 13px;
          text-align: center;
          padding: 20px;
        }
        .b2b-info-card {
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          border: 1px solid #bae6fd;
          border-radius: 16px;
          padding: 24px;
        }
        .b2b-info-card h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 20px 0;
          font-size: 16px;
        }
        .b2b-features {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
        }
        .b2b-feature {
          display: flex;
          gap: 14px;
          align-items: flex-start;
        }
        .feature-icon-box {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          flex-shrink: 0;
        }
        .b2b-feature strong {
          display: block;
          font-size: 14px;
          margin-bottom: 4px;
        }
        .b2b-feature p {
          font-size: 12px;
          color: #6b7280;
          margin: 0;
        }
        .loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 300px;
          color: #6b7280;
        }
        .loading-state p {
          margin-top: 12px;
        }
      `}</style>
    </div>
  );
}

export default EconomicInsightsPage;
