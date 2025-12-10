import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Target,
  DollarSign,
  Activity,
  Zap,
  BarChart3,
  LineChart,
  ShoppingCart,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  Percent,
  Clock,
  Server,
  Users,
  PieChart,
  Rocket,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart as ReLineChart,
  Line,
  BarChart,
  Bar,
  Legend,
} from "recharts";

const API_BASE = "";  // 프록시 사용

/**
 * B2B Market Intelligence Dashboard
 * 
 * 기업 고객(딜러사, 금융사, 렌터카)을 위한 데이터 판매용 인사이트
 * 
 * 핵심 가치:
 * 1. "이 데이터 돈 된다" (수익성)
 * 2. "시장 트렌드를 선점한다" (예측력)
 * 3. "API 하나로 다 된다" (편의성)
 */
function B2BMarketIntelligencePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/b2b/dashboard`);
      const result = await res.json();
      if (result.success) {
        setData(result);
        setLastUpdate(new Date());
        setError(null);
      } else {
        setError(result.error || "데이터 로드 실패");
      }
    } catch (e) {
      setError("API 연결 실패");
      console.error("B2B dashboard error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="page-content">
        <div className="loading-state">
          <RefreshCw className="spin" size={32} />
          <p>Market Intelligence 로딩 중...</p>
        </div>
      </div>
    );
  }

  const moi = data?.market_opportunity || {};
  const buyingSignals = data?.buying_signals || [];
  const sellSignals = data?.sell_signals || [];
  const forecast = data?.forecast_accuracy || {};
  const sensitivity = data?.sensitivity || {};
  const apiStats = data?.api_analytics || {};
  const portfolio = data?.portfolio_roi || {};
  const dataSources = data?.data_sources || {};

  return (
    <div className="page-content b2b-dashboard">
      {/* 헤더 */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1><Rocket size={24} style={{ display: 'inline', marginRight: '8px' }} /> B2B 인사이트</h1>
          <p className="subtitle">중고차 시장 예측 API 대시보드</p>
        </div>
        <div className="header-right">
          <div className="data-source-badges">
            <span className={`source-badge ${dataSources.economic === 'real' ? 'real' : 'sim'}`}>
              경제지표: {dataSources.economic === 'real' ? '🟢 실제' : '🟡 시뮬레이션'}
            </span>
            <span className={`source-badge ${dataSources.database === 'real' ? 'real' : 'sim'}`}>
              DB: {dataSources.database === 'real' ? '🟢 실제' : '🟡 시뮬레이션'}
            </span>
          </div>
          <button className="refresh-btn" onClick={fetchData} disabled={loading}>
            <RefreshCw size={14} className={loading ? "spin" : ""} />
            새로고침
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* KPI 섹션 - 돈 되는 정보 */}
      <div className="kpi-section">
        {/* 거시경제 지표 + 시장 기회 지수 통합 */}
        <div className="kpi-card main combined" style={{ borderColor: moi.color }}>
          <div className="moi-combined">
            {/* 왼쪽: 거시경제 지표 */}
            <div className="macro-indicators">
              <div className="macro-title">현재 거시경제</div>
              <div className="macro-item">
                <span className="macro-label">금리</span>
                <span className="macro-value">{moi.macro?.interest_rate?.value || 3.25}%</span>
                <span className={`macro-status ${moi.macro?.interest_rate?.status || 'neutral'}`}>
                  {moi.macro?.interest_rate?.label || '동결'}
                </span>
              </div>
              <div className="macro-item">
                <span className="macro-label">유가</span>
                <span className="macro-value">${moi.macro?.oil_price?.value || 72}</span>
                <span className={`macro-status ${moi.macro?.oil_price?.status === 'down' ? 'positive' : moi.macro?.oil_price?.status === 'up' ? 'negative' : 'neutral'}`}>
                  {moi.macro?.oil_price?.label || '-'}
                </span>
              </div>
              <div className="macro-item">
                <span className="macro-label">환율</span>
                <span className="macro-value">₩{moi.macro?.exchange_rate?.value?.toLocaleString() || '1,380'}</span>
                <span className={`macro-status ${moi.macro?.exchange_rate?.status === 'down' ? 'positive' : 'negative'}`}>
                  {moi.macro?.exchange_rate?.label || '↑'}
                </span>
              </div>
            </div>
            {/* 오른쪽: MOI 점수 */}
            <div className="moi-score-section">
              <div className="kpi-header">
                <Target size={18} color={moi.color} />
                <span>Market Opportunity</span>
              </div>
              <div className="kpi-value" style={{ color: moi.color }}>
                {moi.score || "--"}
                <span className="kpi-suffix">/100</span>
              </div>
              <div className="kpi-signal" style={{ background: `${moi.color}20`, color: moi.color }}>
                {moi.signal || "Loading"} - {moi.signal_kr || ""}
              </div>
            </div>
          </div>
        </div>

        {/* 매집 추천 TOP */}
        <div className="kpi-card buy">
          <div className="kpi-header">
            <ShoppingCart size={20} color="#22c55e" />
            <span>Hot Buying Signal</span>
          </div>
          {buyingSignals[0] && (
            <>
              <div className="kpi-model">{buyingSignals[0].model}</div>
              <div className="kpi-roi positive">
                <ArrowUpRight size={18} />
                ROI +{buyingSignals[0].expected_roi}% 예상
              </div>
              <div className="kpi-meta">
                회전율 {buyingSignals[0].turnover_weeks}주 | {buyingSignals[0].reason}
              </div>
            </>
          )}
        </div>

        {/* 매각 경고 TOP */}
        <div className="kpi-card sell">
          <div className="kpi-header">
            <AlertTriangle size={20} color="#ef4444" />
            <span>Sell Alert</span>
          </div>
          {sellSignals[0] && (
            <>
              <div className="kpi-model">{sellSignals[0].model}</div>
              <div className="kpi-roi negative">
                <ArrowDownRight size={18} />
                시세 -{sellSignals[0].expected_drop}% 예상
              </div>
              <div className="kpi-meta">
                위험도 {sellSignals[0].risk_score} | {sellSignals[0].reason}
              </div>
            </>
          )}
        </div>

        {/* 포트폴리오 ROI */}
        <div className="kpi-card portfolio">
          <div className="kpi-header">
            <PieChart size={20} color="#8b5cf6" />
            <span>Portfolio ROI</span>
          </div>
          <div className="kpi-value purple">
            +{portfolio.portfolios?.balanced?.roi?.toFixed(1) || "--"}%
            <span className="kpi-suffix">예상</span>
          </div>
          <div className="kpi-meta">
            권장: {portfolio.portfolios?.[portfolio.recommended]?.name || "균형형"} 포트폴리오
          </div>
          <div className="kpi-meta">
            시장 국면: {portfolio.market_phase || "일반"}
          </div>
        </div>
      </div>

      {/* 메인 차트 섹션 */}
      <div className="chart-section">
        {/* 예측 정확도 차트 */}
        <div className="chart-card main-chart">
          <div className="chart-header">
            <h3>
              <LineChart size={18} />
              📈 과거 예측 정확도 (Backtest)
            </h3>
            <div className="accuracy-badge">
              <CheckCircle size={14} color="#22c55e" />
              정확도 {forecast.accuracy || "--"}%
            </div>
          </div>
          <div className="chart-desc">
            ※ 이 차트는 <strong>과거</strong> 예측값과 실제 시세를 비교한 백테스트 결과입니다.
            <br />※ MOI 점수({moi.score})는 <strong>현재</strong> 시장 매수 적기 지수입니다. (다른 지표)
          </div>
          <div className="chart-body">
            <ResponsiveContainer width="100%" height={220}>
              <ReLineChart data={forecast.history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#666" }} />
                <YAxis tick={{ fontSize: 11, fill: "#666" }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{
                    background: "white",
                    border: "none",
                    borderRadius: "8px",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="실제 시세지수"
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="과거 예측값"
                />
              </ReLineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-insight">
            <Zap size={14} color="#f59e0b" />
            <span>{forecast.insight || "분석 중..."}</span>
          </div>
          <div className="chart-avoided-loss">
            💡 회피 손실액: 약 <strong>{forecast.avoided_loss || 0}억원</strong> (시뮬레이션 기준)
          </div>
        </div>

        {/* API 사용 현황 */}
        <div className="chart-card api-stats">
          <div className="chart-header">
            <h3>
              <Server size={18} />
              🔗 API Usage Analytics
            </h3>
          </div>
          <div className="api-metrics">
            <div className="metric">
              <div className="metric-value">{apiStats.daily_calls || 0}</div>
              <div className="metric-label">오늘 분석</div>
            </div>
            <div className="metric">
              <div className="metric-value">{apiStats.monthly_calls || 0}</div>
              <div className="metric-label">전체 분석</div>
            </div>
            <div className="metric">
              <div className="metric-value">{apiStats.avg_latency_ms || "--"}ms</div>
              <div className="metric-label">평균 응답</div>
            </div>
            <div className="metric">
              <div className="metric-value">{apiStats.active_users || 1}</div>
              <div className="metric-label">활성 사용자</div>
            </div>
          </div>
          <div className="use-cases">
            <div className="use-case-title">
              <Users size={14} />
              Top Use Cases
            </div>
            {apiStats.use_cases && Object.entries(apiStats.use_cases).map(([key, value]) => (
              <div key={key} className="use-case-item">
                <span className="use-case-name">
                  {key === 'price_prediction' ? '시세 예측' :
                   key === 'deal_analysis' ? '매물 분석' :
                   key === 'negotiation' ? '네고 대본' :
                   key === 'dynamic_pricing' ? '동적 가격 책정' :
                   key === 'inventory_risk' ? '재고 리스크 관리' : '대출 심사 로직'}
                </span>
                <div className="use-case-bar">
                  <div className="bar-fill" style={{ width: `${value}%` }}></div>
                </div>
                <span className="use-case-pct">{value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 매집/매각 시그널 테이블 */}
      <div className="signals-section">
        {/* 매집 추천 */}
        <div className="signal-table">
          <h3>
            <ShoppingCart size={18} color="#22c55e" />
            Buying Signals (매집 추천)
          </h3>
          <table>
            <thead>
              <tr>
                <th>모델</th>
                <th>예상 ROI</th>
                <th>관심도</th>
                <th>신호</th>
                <th>사유</th>
              </tr>
            </thead>
            <tbody>
              {buyingSignals.map((item, idx) => (
                <tr key={idx}>
                  <td className="model-cell">
                    {item.model}
                    {item.data_source === 'real' && <span className="real-badge">실제</span>}
                  </td>
                  <td className={`roi-cell ${item.expected_roi > 8 ? 'positive' : ''}`}>
                    +{item.expected_roi}%
                  </td>
                  <td>{item.interest_score ? `${item.interest_score}회` : (item.turnover_weeks ? `${item.turnover_weeks}주` : '-')}</td>
                  <td>
                    <span className={`signal-badge ${item.signal}`}>
                      {item.signal === 'buy' ? 'BUY' : item.signal === 'hold' ? 'HOLD' : item.signal === 'watch' ? 'WATCH' : 'AVOID'}
                    </span>
                  </td>
                  <td className="reason-cell">{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 매각 경고 */}
        <div className="signal-table sell">
          <h3>
            <AlertTriangle size={18} color="#ef4444" />
            Sell Signals (매각 경고)
          </h3>
          <table>
            <thead>
              <tr>
                <th>모델</th>
                <th>위험도</th>
                <th>예상 하락</th>
                <th>위험 수준</th>
                <th>사유</th>
              </tr>
            </thead>
            <tbody>
              {sellSignals.map((item, idx) => (
                <tr key={idx}>
                  <td className="model-cell">
                    {item.model}
                    {item.data_source === 'real' && <span className="real-badge">실제</span>}
                  </td>
                  <td>{item.risk_score}</td>
                  <td className="negative">-{item.expected_drop}%</td>
                  <td>
                    <span className={`risk-badge ${item.risk_level}`}>
                      {item.risk_level === 'high' ? 'HIGH' : item.risk_level === 'medium' ? 'MED' : 'LOW'}
                    </span>
                  </td>
                  <td className="reason-cell">{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 민감도 분석 */}
      <div className="sensitivity-section">
        <h3>
          <BarChart3 size={18} />
          📊 Macro Sensitivity Analysis (민감도 분석)
        </h3>
        <div className="sensitivity-content">
          <div className="sensitivity-table">
            <table>
              <thead>
                <tr>
                  <th>세그먼트</th>
                  <th>금리 민감도</th>
                  <th>유가 민감도</th>
                  <th>환율 민감도</th>
                </tr>
              </thead>
              <tbody>
                {sensitivity.segments?.slice(0, 6).map((seg, idx) => (
                  <tr key={idx}>
                    <td>{seg.segment_name}</td>
                    <td className={seg.interest_rate_impact < 0 ? 'negative' : 'positive'}>
                      {seg.interest_rate_impact > 0 ? '+' : ''}{seg.interest_rate_impact.toFixed(1)}%
                    </td>
                    <td className={seg.oil_price_impact < 0 ? 'negative' : 'positive'}>
                      {seg.oil_price_impact > 0 ? '+' : ''}{seg.oil_price_impact.toFixed(1)}%
                    </td>
                    <td className={seg.exchange_rate_impact < 0 ? 'negative' : 'positive'}>
                      {seg.exchange_rate_impact > 0 ? '+' : ''}{seg.exchange_rate_impact.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="scenarios">
            <h4>시나리오 분석</h4>
            {sensitivity.scenarios?.map((scenario, idx) => (
              <div key={idx} className="scenario-card">
                <div className="scenario-name">{scenario.name}</div>
                <div className="scenario-condition">{scenario.condition}</div>
                <div className="scenario-impact">{scenario.impact}</div>
                <div className="scenario-recommendation">
                  <CheckCircle size={12} color="#22c55e" />
                  {scenario.recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="dashboard-footer">
        <div className="footer-left">
          마지막 업데이트: {lastUpdate?.toLocaleString("ko-KR") || "--"}
        </div>
        <div className="footer-right">
          <span className="data-notice">
            * 본 데이터는 B2B 기업 고객용 인사이트입니다. 투자 결정은 자체 판단에 따라 진행하세요.
          </span>
        </div>
      </div>

      <style>{`
        .b2b-dashboard {
          background: #f8fafc;
          min-height: 100vh;
          padding: 16px 20px;
        }
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin: 0 0 16px 0;
          padding: 0 0 12px 0;
          border-bottom: 1px solid #e2e8f0;
        }
        .header-left h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 700;
          background: linear-gradient(135deg, #1e40af, #7c3aed);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .subtitle {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 13px;
        }
        .header-right {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .data-source-badges {
          display: flex;
          gap: 8px;
        }
        .source-badge {
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 500;
        }
        .source-badge.real {
          background: #dcfce7;
          color: #166534;
        }
        .source-badge.sim {
          background: #fef3c7;
          color: #92400e;
        }
        .refresh-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: white;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.2s;
        }
        .refresh-btn:hover {
          background: #f1f5f9;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
       /* KPI Section 수정 */
/* KPI Section 수정 */
.kpi-section {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 16px;
  margin: 0 0 20px 0;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}
        .kpi-card {
          background: white;
          border-radius: 12px;
          padding: 14px 16px;
          border: 1px solid #e2e8f0;
          transition: all 0.2s;
          min-height: auto;
          box-sizing: border-box;
        }
        .kpi-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .kpi-card.main {
          /* border-left는 기본 1px solid 유지 */
        }
/* 첫 번째 카드 설정 단순화 */
.kpi-card.main.combined {
  border-top: 3px solid;
  grid-column: 1; /* 강제로 1번 컬럼 시작 지정 */
  justify-self: start; /* 왼쪽 정렬 강제 */
  width: 100%; /* 너비 꽉 채우기 */
  margin-left: 0; /* 마진 제거 */
}
        .moi-combined {
          display: flex;
          gap: 0;
          width: 100%;
          align-items: stretch;
          margin: 0;
        }
        .macro-indicators {
          flex: 1;
          border-right: 1px solid #e2e8f0;
          padding-right: 12px;
          margin-right: 12px;
        }
        .macro-title {
          font-size: 11px;
          font-weight: 600;
          color: #64748b;
          margin-bottom: 10px;
        }
        .macro-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 6px;
          font-size: 12px;
        }
        .macro-label {
          color: #64748b;
          width: 32px;
        }
        .macro-value {
          font-weight: 600;
          color: #1e293b;
          flex: 1;
        }
        .macro-status {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 4px;
        }
        .macro-status.positive { background: #dcfce7; color: #16a34a; }
        .macro-status.negative { background: #fee2e2; color: #dc2626; }
        .macro-status.neutral { background: #f1f5f9; color: #64748b; }
        .moi-score-section {
          flex: 1;
          text-align: center;
        }
        .moi-score-section .kpi-value {
          font-size: 36px;
        }
        .kpi-header {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          color: #64748b;
          margin-bottom: 8px;
        }
        .kpi-value {
          font-size: 32px;
          font-weight: 700;
          line-height: 1;
          margin-bottom: 6px;
        }
        .kpi-value.purple { color: #8b5cf6; }
        .kpi-suffix {
          font-size: 14px;
          color: #94a3b8;
          margin-left: 2px;
        }
        .kpi-signal {
          display: inline-block;
          padding: 3px 10px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 600;
          margin-bottom: 8px;
        }
        .kpi-factors {
          font-size: 10px;
          color: #64748b;
          line-height: 1.4;
        }
        .factor-item {
          margin: 2px 0;
        }
        .kpi-model {
          font-size: 16px;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 4px;
        }
        .kpi-roi {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 4px;
        }
        .kpi-roi.positive { color: #22c55e; }
        .kpi-roi.negative { color: #ef4444; }
        .kpi-meta {
          font-size: 10px;
          color: #64748b;
          margin-top: 2px;
        }
        
        /* Chart Section */
        .chart-section {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 20px;
          margin-bottom: 24px;
        }
        .chart-card {
          background: white;
          border-radius: 16px;
          padding: 20px;
          border: 1px solid #e2e8f0;
        }
        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        .chart-desc {
          font-size: 11px;
          color: #64748b;
          background: #f8fafc;
          padding: 8px 12px;
          border-radius: 6px;
          margin-bottom: 12px;
          line-height: 1.5;
        }
        .chart-desc strong {
          color: #3b82f6;
        }
        .chart-header h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0;
          font-size: 16px;
        }
        .accuracy-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 6px 12px;
          background: #f0fdf4;
          border: 1px solid #86efac;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          color: #16a34a;
        }
        .chart-insight {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: #fffbeb;
          border-radius: 8px;
          font-size: 13px;
          color: #92400e;
          margin-top: 12px;
        }
        .chart-avoided-loss {
          margin-top: 8px;
          padding: 8px 12px;
          background: #f0fdf4;
          border-radius: 8px;
          font-size: 12px;
          color: #166534;
        }
        
        /* API Stats */
        .api-metrics {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          margin-bottom: 20px;
        }
        .metric {
          background: #f8fafc;
          border-radius: 12px;
          padding: 16px;
          text-align: center;
        }
        .metric-value {
          font-size: 24px;
          font-weight: 700;
          color: #1e293b;
        }
        .metric-label {
          font-size: 11px;
          color: #64748b;
          margin-top: 4px;
        }
        .use-cases {
          border-top: 1px solid #e2e8f0;
          padding-top: 16px;
        }
        .use-case-title {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 600;
          margin-bottom: 12px;
        }
        .use-case-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-size: 12px;
        }
        .use-case-name {
          width: 100px;
          color: #64748b;
        }
        .use-case-bar {
          flex: 1;
          height: 8px;
          background: #e2e8f0;
          border-radius: 4px;
          overflow: hidden;
        }
        .bar-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #8b5cf6);
          border-radius: 4px;
        }
        .use-case-pct {
          width: 35px;
          text-align: right;
          font-weight: 600;
          color: #3b82f6;
        }
        
        /* Signal Tables */
        .signals-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 24px;
        }
        .signal-table {
          background: white;
          border-radius: 16px;
          padding: 20px;
          border: 1px solid #e2e8f0;
        }
        .signal-table h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 16px;
          font-size: 15px;
        }
        .signal-table table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
        }
        .signal-table th {
          text-align: left;
          padding: 8px;
          border-bottom: 2px solid #e2e8f0;
          color: #64748b;
          font-weight: 600;
        }
        .signal-table td {
          padding: 10px 8px;
          border-bottom: 1px solid #f1f5f9;
        }
        .model-cell {
          font-weight: 600;
          color: #1e293b;
        }
        .real-badge {
          display: inline-block;
          margin-left: 6px;
          padding: 2px 6px;
          background: #dbeafe;
          color: #1d4ed8;
          font-size: 9px;
          font-weight: 600;
          border-radius: 4px;
          vertical-align: middle;
        }
        .roi-cell.positive { color: #22c55e; font-weight: 600; }
        .negative { color: #ef4444; }
        .reason-cell {
          color: #64748b;
          font-size: 11px;
        }
        .signal-badge {
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 700;
        }
        .signal-badge.buy { background: #dcfce7; color: #16a34a; }
        .signal-badge.hold { background: #fef3c7; color: #d97706; }
        .signal-badge.watch { background: #e0e7ff; color: #4338ca; }
        .signal-badge.avoid { background: #fee2e2; color: #dc2626; }
        .risk-badge {
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 700;
        }
        .risk-badge.high { background: #fee2e2; color: #dc2626; }
        .risk-badge.medium { background: #fef3c7; color: #d97706; }
        .risk-badge.low { background: #dcfce7; color: #16a34a; }
        
        /* Sensitivity */
        .sensitivity-section {
          background: white;
          border-radius: 16px;
          padding: 20px;
          border: 1px solid #e2e8f0;
          margin-bottom: 24px;
        }
        .sensitivity-section h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 16px;
          font-size: 16px;
        }
        .sensitivity-content {
          display: grid;
          grid-template-columns: 1.5fr 1fr;
          gap: 20px;
        }
        .sensitivity-table table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
        }
        .sensitivity-table th {
          text-align: left;
          padding: 10px 8px;
          background: #f8fafc;
          border-bottom: 2px solid #e2e8f0;
        }
        .sensitivity-table td {
          padding: 10px 8px;
          border-bottom: 1px solid #f1f5f9;
        }
        .sensitivity-table .positive { color: #22c55e; }
        .sensitivity-table .negative { color: #ef4444; }
        .scenarios h4 {
          margin: 0 0 12px;
          font-size: 14px;
        }
        .scenario-card {
          background: #f8fafc;
          border-radius: 10px;
          padding: 12px;
          margin-bottom: 10px;
        }
        .scenario-name {
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 4px;
        }
        .scenario-condition {
          font-size: 11px;
          color: #3b82f6;
          margin-bottom: 4px;
        }
        .scenario-impact {
          font-size: 12px;
          color: #64748b;
          margin-bottom: 6px;
        }
        .scenario-recommendation {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 11px;
          color: #16a34a;
        }
        
        /* Footer */
        .dashboard-footer {
          display: flex;
          justify-content: space-between;
          padding: 16px 0;
          border-top: 1px solid #e2e8f0;
          font-size: 11px;
          color: #94a3b8;
        }
        .data-notice {
          font-style: italic;
        }
        
        .loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 400px;
          color: #64748b;
        }
        .loading-state p {
          margin-top: 12px;
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
      `}</style>
    </div>
  );
}

export default B2BMarketIntelligencePage;
