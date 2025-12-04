# 📡 Car-Sentix API 명세서

> **Base URL**: `http://localhost:8000`  
> **최종 업데이트**: 2024년 12월 4일  
> **작성 원칙**: 실제 run_server.py 기반

---

## 목차

1. [헬스체크](#1-헬스체크)
2. [가격 예측](#2-가격-예측)
3. [타이밍 분석](#3-타이밍-분석)
4. [B2B 인사이트](#4-b2b-인사이트)
5. [추천/유사 차량](#5-추천유사-차량)
6. [관리자 API](#6-관리자-api)
7. [에러 응답](#7-에러-응답)

---

## 1. 헬스체크

### GET /api/health

기본 헬스체크

**Response**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "message": "Car-Sentix API"
}
```

### GET /api/health/detailed

상세 헬스체크 (모든 서비스 상태)

**Response**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "response_time_ms": 45.2,
  "services": {
    "prediction": {"status": "healthy", "message": "OK"},
    "timing": {"status": "healthy", "message": "OK"},
    "groq_ai": {"status": "healthy", "message": "Connected"},
    "database": {"status": "healthy", "message": "OK"},
    "recommendation": {"status": "healthy", "message": "OK"}
  }
}
```

---

## 2. 가격 예측

### POST /api/predict

단순 가격 예측

**Request Body**
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "has_sunroof": true,
  "has_navigation": true,
  "has_leather_seat": false,
  "has_smart_key": true,
  "has_rear_camera": true
}
```

**Parameters**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| brand | string | ✅ | 제조사 (현대, 기아, BMW 등) |
| model | string | ✅ | 모델명 (그랜저, K5 등) |
| year | int | ✅ | 연식 (1990-2026) |
| mileage | int | ✅ | 주행거리 (km, 0-1,000,000) |
| fuel | string | ❌ | 연료 (가솔린/디젤/LPG/하이브리드/전기) |
| has_* | bool | ❌ | 옵션 여부 |

**Response**
```json
{
  "predicted_price": 3200.5,
  "price_range": [2900.0, 3500.0],
  "confidence": 0.87
}
```

### POST /api/smart-analysis

통합 분석 (가격 + 타이밍 + AI)

**Request Body**
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "has_sunroof": true,
  "has_navigation": true,
  "has_leather_seat": false,
  "has_smart_key": true,
  "has_rear_camera": true,
  "has_heated_seat": false,
  "has_ventilated_seat": false,
  "has_led_lamp": true,
  "is_accident_free": true,
  "inspection_grade": "good",
  "sale_price": 3300,
  "dealer_description": "무사고, 1인 신조",
  "detail_url": "https://encar.com/..."
}
```

**추가 Parameters**
| 필드 | 타입 | 설명 |
|------|------|------|
| inspection_grade | string | 성능점검 등급 (normal/good/excellent) |
| sale_price | int | 판매가 (만원, AI 분석용) |
| dealer_description | string | 딜러 설명 (허위매물 탐지용) |
| detail_url | string | 매물 URL |

**Response**
```json
{
  "prediction": {
    "predicted_price": 3200.5,
    "price_range": [2900.0, 3500.0],
    "confidence": 0.87
  },
  "timing": {
    "timing_score": 65,
    "label": "괜찮은 시기",
    "breakdown": {
      "macro": 60,
      "trend": 70,
      "schedule": 65
    },
    "reasons": [
      "✅ 기준금리 3.25% (안정)",
      "✅ 검색량 증가 추세",
      "⚠️ 신차 출시 2개월 후 예정"
    ]
  },
  "groq_analysis": {
    "negotiation": {
      "script": "이 차량은 시세 대비 약 100만원 높습니다...",
      "points": ["주행거리 대비 가격 높음", "옵션 대비 가격 적정"]
    }
  }
}
```

---

## 3. 타이밍 분석

### POST /api/timing

모델별 타이밍 분석

**Request Body**
```json
{
  "model": "그랜저"
}
```

**Response**
```json
{
  "timing_score": 65,
  "label": "괜찮은 시기",
  "breakdown": {
    "macro": 60,
    "trend": 70,
    "schedule": 65
  },
  "reasons": [
    "✅ 기준금리 3.25% 동결",
    "✅ 유가 $60 (안정)",
    "✅ 검색량 전주 대비 +5%"
  ]
}
```

### GET /api/market-timing

시장 전체 타이밍 (홈화면용)

**Response**
```json
{
  "success": true,
  "score": 65,
  "label": "괜찮은 시기",
  "color": "blue",
  "emoji": "🔵",
  "action": "매수 고려",
  "indicators": [
    {"name": "금리", "status": "positive", "desc": "낮은 금리"},
    {"name": "유가", "status": "positive", "desc": "안정세"},
    {"name": "신차출시", "status": "neutral", "desc": "영향 적음"}
  ],
  "reasons": ["✅ 기준금리 안정", "✅ 유가 하락세"],
  "updated_at": "2024-12-04T16:30:00",
  "message": "경제지표 분석 결과, 괜찮은 시기"
}
```

### GET /api/economic-insights

경제 인사이트 (Phase 3)

**Response**
```json
{
  "success": true,
  "current_score": 65,
  "economic_indicators": {
    "oil": {
      "current": 72.5,
      "change_pct": -2.3,
      "trend": "down",
      "signal": "buy",
      "source": "yahoo_finance"
    },
    "exchange": {
      "current": 1380.5,
      "change_pct": 1.2,
      "trend": "up",
      "signal": "hold",
      "source": "yahoo_finance"
    },
    "interest": {
      "current": 3.25,
      "days_until_meeting": 15,
      "signal": "hold"
    }
  },
  "prediction": {
    "chart_data": [
      {"date": "12/04", "score": 65},
      {"date": "12/05", "score": 66},
      ...
    ],
    "this_week": {"avg_score": 65, "best_day": "2024-12-06"},
    "next_week": {"avg_score": 67},
    "recommendation": "이번 주 금요일이 최적 구매일입니다"
  },
  "regional": {
    "region": "서울",
    "demand_index": 95,
    "price_premium": 5,
    "recommendation": "경기/인천 지역 매물 검토 권장"
  }
}
```

### GET /api/timing-prediction

향후 2주 예측

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| days | int | 14 | 예측 기간 (일) |

**Response**
```json
{
  "success": true,
  "predictions": [
    {"date": "2024-12-04", "score": 65, "factors": ["금통위 2주 전"]},
    {"date": "2024-12-05", "score": 66, "factors": ["주말 전"]},
    ...
  ],
  "best_day": "2024-12-06",
  "worst_day": "2024-12-08"
}
```

### GET /api/regional-analysis

지역별 수요 분석

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| region | string | "전국" | 지역명 |
| vehicle_type | string | null | 차종 (SUV/세단/경차/전기차) |

**Response**
```json
{
  "success": true,
  "region": "서울",
  "demand_index": 95,
  "price_premium": 5,
  "vehicle_preferences": {
    "SUV": 1.2,
    "세단": 1.0,
    "경차": 0.8
  },
  "nearby_alternatives": [
    {"region": "경기", "demand_index": 100, "price_premium": 3},
    {"region": "인천", "demand_index": 85, "price_premium": 0}
  ],
  "recommendation": "경기/인천 지역 매물 검토 권장"
}
```

---

## 4. B2B 인사이트

### GET /api/b2b/dashboard

B2B 대시보드 전체 데이터

**Response**
```json
{
  "success": true,
  "market_opportunity": {
    "score": 72.5,
    "signal": "Buy",
    "signal_kr": "매집 권장",
    "color": "#3b82f6",
    "factors": [
      "유가 하락세 $72.5 (-2.3%)",
      "기준금리 3.25% 유지 중",
      "연말/연초 매물 증가"
    ],
    "data_source": "real"
  },
  "buying_signals": [
    {
      "model": "팰리세이드",
      "segment": "large_suv",
      "avg_price": 4500,
      "expected_roi": 17.2,
      "turnover_weeks": 2.5,
      "demand_trend": "rising",
      "signal": "buy",
      "reason": "수요 상승 추세, ROI 12% 이상 예상"
    },
    ...
  ],
  "sell_signals": [
    {
      "model": "제네시스 G80",
      "segment": "luxury",
      "risk_score": 78.5,
      "expected_drop": 12.3,
      "risk_level": "high",
      "reason": "신차 출시 영향, 금리 민감 구간"
    },
    ...
  ],
  "portfolio_roi": {
    "portfolios": {
      "aggressive": {"name": "공격형", "roi": 15.2, "risk": "high"},
      "balanced": {"name": "균형형", "roi": 9.5, "risk": "medium"},
      "conservative": {"name": "안정형", "roi": 5.8, "risk": "low"}
    },
    "recommended": "balanced",
    "market_phase": "일반"
  },
  "forecast_accuracy": {
    "accuracy": 94.2,
    "history": [
      {"date": "11/20", "predicted": 52.3, "actual": 51.8, "error": 0.5},
      ...
    ],
    "avoided_loss": 15.2,
    "insight": "지난달 매각 신호 적중률 94.2%, 회피 손실액 약 15억원"
  },
  "sensitivity": {
    "segments": [
      {
        "segment": "luxury",
        "segment_name": "고급차",
        "interest_rate_impact": -20.0,
        "oil_price_impact": -3.0,
        "exchange_rate_impact": -8.0
      },
      ...
    ],
    "scenarios": [
      {
        "name": "금리 인상 시나리오",
        "condition": "기준금리 +0.25%p",
        "impact": "대형 세단 수요 -12%, 고급차 -15% 예상",
        "recommendation": "대형 세단/고급차 재고 축소 권장"
      },
      ...
    ]
  },
  "api_analytics": {
    "daily_calls": 52400,
    "monthly_calls": 1245000,
    "avg_latency_ms": 45.2,
    "uptime": 99.97,
    "enterprise_clients": 12,
    "use_cases": {
      "dynamic_pricing": 45,
      "inventory_risk": 30,
      "loan_approval": 25
    }
  },
  "data_sources": {
    "economic": "real",
    "database": "simulated",
    "vehicle_stats": "simulated"
  },
  "generated_at": "2024-12-04T16:30:00"
}
```

### GET /api/b2b/market-opportunity

시장 기회 지수만 조회

### GET /api/b2b/buying-signals

매집 추천 목록

**Query Parameters**
| 파라미터 | 타입 | 기본값 |
|----------|------|--------|
| limit | int | 5 |

### GET /api/b2b/sell-signals

매각 경고 목록

### GET /api/b2b/sensitivity

민감도 분석

### GET /api/b2b/forecast-accuracy

예측 정확도

### GET /api/b2b/api-analytics

API 사용 현황

---

## 5. 추천/유사 차량

### GET /api/popular

인기 모델

**Query Parameters**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| category | string | "all" | domestic/imported/all |
| limit | int | 5 | 개수 |

**Response**
```json
{
  "models": [
    {"rank": 1, "brand": "현대", "model": "그랜저", "count": 1234},
    {"rank": 2, "brand": "기아", "model": "K5", "count": 1100},
    ...
  ]
}
```

### GET /api/trending

최근 인기 검색 모델

**Query Parameters**
| 파라미터 | 타입 | 기본값 |
|----------|------|--------|
| days | int | 7 |
| limit | int | 10 |

### GET /api/recommendations

사용자 맞춤 추천

**Query Parameters**
| 파라미터 | 타입 | 기본값 |
|----------|------|--------|
| user_id | string | "guest" |
| category | string | "all" |
| budget_min | int | null |
| budget_max | int | null |
| limit | int | 10 |

### GET /api/good-deals

가성비 좋은 차량 (예측가 > 실제가)

### POST /api/similar

유사 차량 검색

**Request Body**
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "predicted_price": 3200
}
```

**Response**
```json
{
  "similar_vehicles": [
    {
      "brand": "현대",
      "model": "그랜저",
      "year": 2022,
      "mileage": 38000,
      "price": 3100,
      "gap_percent": -3.1
    },
    ...
  ],
  "price_distribution": {
    "min": 2800,
    "max": 3600,
    "median": 3200,
    "count": 45
  }
}
```

---

## 6. 관리자 API

### GET /api/admin/stats

대시보드 통계

**Response**
```json
{
  "total_analyses": 12345,
  "today_analyses": 234,
  "unique_users": 567,
  "popular_models": [...],
  "hourly_distribution": [...]
}
```

### GET /api/admin/recent-analyses

최근 분석 목록

**Query Parameters**
| 파라미터 | 타입 | 기본값 |
|----------|------|--------|
| limit | int | 20 |
| offset | int | 0 |

### GET /api/notifications

알림 목록

**Query Parameters**
| 파라미터 | 타입 | 기본값 |
|----------|------|--------|
| limit | int | 20 |
| unread_only | bool | false |

### PUT /api/notifications/{id}/read

알림 읽음 처리

---

## 7. 에러 응답

### 공통 에러 형식

```json
{
  "success": false,
  "error": "에러 메시지",
  "detail": "상세 설명 (선택)"
}
```

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파라미터 오류) |
| 404 | 리소스 없음 |
| 500 | 서버 내부 오류 |

### 예측 실패 시

```json
{
  "predicted_price": 0,
  "price_range": [0, 0],
  "confidence": 0,
  "error": "해당 모델의 학습 데이터가 없습니다"
}
```

---

*이 문서는 run_server.py의 실제 API 정의를 기반으로 작성되었습니다.*
