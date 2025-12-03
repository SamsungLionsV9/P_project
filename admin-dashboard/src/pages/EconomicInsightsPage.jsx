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
} from "lucide-react";

const API_BASE = "http://localhost:8000";

/**
 * 경제지표 인사이트 페이지 (차별화 포인트)
 * - 실시간 경제지표 모니터링
 * - 시장 타이밍 분석 현황
 * - B2B 데이터 서비스 확장 기반
 */
function EconomicInsightsPage() {
  const [marketTiming, setMarketTiming] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // 시장 타이밍 데이터 로드
  const fetchMarketTiming = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/market-timing`);
      const data = await res.json();
      setMarketTiming(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (e) {
      setError("시장 타이밍 데이터를 불러올 수 없습니다");
      console.error("Market timing fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketTiming();
    // 5분마다 자동 갱신
    const interval = setInterval(fetchMarketTiming, 5 * 60 * 1000);
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
        <button className="refresh-btn" onClick={fetchMarketTiming} disabled={loading}>
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
