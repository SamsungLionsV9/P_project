# 📊 Car-Sentix 데이터 구조 명세

> **최종 업데이트**: 2024년 12월 4일  
> **작성 원칙**: 실제 코드/파일 기반 사실만 기록

---

## 1. ML 모델 데이터

### 1.1 학습 데이터 (CSV)

**위치**: `data/`

```
data/
├── encar_domestic_cleaned.csv    # 국산차 학습 데이터
├── encar_imported_cleaned.csv    # 수입차 학습 데이터
├── encar_all_data.csv            # 전체 원본
└── encar_full_*.csv              # 전처리 중간 파일
```

**국산차 데이터 스키마** (encar_domestic_cleaned.csv)

| 컬럼명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| brand | string | 제조사 | 현대 |
| model | string | 모델명 | 그랜저 |
| year | int | 연식 | 2022 |
| mileage | int | 주행거리 (km) | 35000 |
| fuel | string | 연료 | 가솔린 |
| price | int | 가격 (만원) | 3200 |
| has_sunroof | bool | 선루프 | True |
| has_navigation | bool | 네비게이션 | True |
| has_leather_seat | bool | 가죽시트 | False |
| has_smart_key | bool | 스마트키 | True |
| has_rear_camera | bool | 후방카메라 | True |
| has_heated_seat | bool | 열선시트 | False |
| has_ventilated_seat | bool | 통풍시트 | False |
| has_led_lamp | bool | LED 램프 | True |
| accident_free | bool | 무사고 | True |

**데이터 통계 (사실)**
| 구분 | 건수 | 브랜드 수 | 모델 수 |
|------|------|----------|---------|
| 국산차 | 119,343 | 5 | 253 |
| 수입차 | ~45,000 | 30+ | 180 |

### 1.2 모델 파일 (PKL)

**위치**: `models/`

```
models/
├── domestic_unified_v12_gasoline.pkl      # 국산 가솔린 모델
├── domestic_unified_v12_diesel.pkl        # 국산 디젤 모델
├── domestic_unified_v12_lpg.pkl           # 국산 LPG 모델
├── domestic_unified_v12_hybrid.pkl        # 국산 하이브리드 모델
├── domestic_unified_v12_ev.pkl            # 국산 전기 모델
├── domestic_unified_v12_encoders.pkl      # 국산차 인코더
├── domestic_unified_v12_features.pkl      # 국산차 Feature 목록
│
├── imported_unified_v14_gasoline.pkl      # 수입 가솔린 모델
├── imported_unified_v14_diesel.pkl        # 수입 디젤 모델
├── imported_unified_v14_hybrid.pkl        # 수입 하이브리드 모델
├── imported_unified_v14_ev.pkl            # 수입 전기 모델
├── imported_unified_v14_encoders.pkl      # 수입차 인코더
└── imported_unified_v14_features.pkl      # 수입차 Feature 목록
```

**모델 구조 (XGBoost)**
```python
# domestic_unified_v12_*.pkl 내부
{
    'model': XGBRegressor,          # 학습된 XGBoost 모델
    'feature_names': ['brand_encoded', 'model_encoded', 'year', 'mileage', ...],
    'target_column': 'price',
    'train_date': '2024-11-28',
    'metrics': {
        'r2_score': 0.87,
        'mae': 231,
        'rmse': 312
    }
}
```

**인코더 구조** (encoders.pkl)
```python
{
    'brand_encoder': LabelEncoder,   # 브랜드 → 숫자
    'model_encoder': LabelEncoder,   # 모델 → 숫자
    'fuel_encoder': LabelEncoder     # 연료 → 숫자
}
```

**Feature 목록** (features.pkl)
```python
[
    'brand_encoded',
    'model_encoded',
    'year',
    'mileage',
    'fuel_encoded',
    'has_sunroof',
    'has_navigation',
    'has_leather_seat',
    'has_smart_key',
    'has_rear_camera',
    'has_heated_seat',
    'has_ventilated_seat',
    'has_led_lamp',
    'is_accident_free'
]
```

---

## 2. 데이터베이스 (SQLite)

### 2.1 파일 위치

**위치**: `data/carsentix.db`

### 2.2 테이블 스키마

#### analyses (분석 이력)

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'guest',
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    fuel_type TEXT,
    predicted_price REAL,
    actual_price INTEGER,
    confidence REAL,
    timing_score INTEGER,
    signal TEXT,
    detail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_analyses_user ON analyses(user_id);
CREATE INDEX idx_analyses_model ON analyses(brand, model);
CREATE INDEX idx_analyses_date ON analyses(created_at);
```

**예시 데이터**
```json
{
  "id": 1234,
  "user_id": "guest",
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel_type": "가솔린",
  "predicted_price": 3200.5,
  "actual_price": 3300,
  "confidence": 0.87,
  "timing_score": 65,
  "signal": "buy",
  "detail_url": "https://encar.com/...",
  "created_at": "2024-12-04 16:30:00"
}
```

#### notifications (알림)

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'guest',
    type TEXT NOT NULL,           -- 'fraud_alert', 'price_drop', etc.
    title TEXT NOT NULL,
    message TEXT,
    data TEXT,                    -- JSON 문자열
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
```

#### search_history (검색 이력)

```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'guest',
    brand TEXT,
    model TEXT,
    search_type TEXT,             -- 'predict', 'timing', 'similar'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. 외부 데이터 소스

### 3.1 Yahoo Finance (실제 데이터)

**수집 주기**: API 호출 시 실시간

**유가 (WTI)**
```python
# 데이터 형식
{
    "ticker": "CL=F",
    "current": 72.5,           # 현재가 (USD/배럴)
    "history": [               # 60일 히스토리
        {"date": "2024-10-05", "close": 75.2},
        {"date": "2024-10-06", "close": 74.8},
        ...
    ],
    "ma7": 73.5,               # 7일 이동평균
    "ma30": 74.2,              # 30일 이동평균
    "change_pct_week": -2.1,   # 주간 변화율
    "change_pct_month": -3.5   # 월간 변화율
}
```

**환율 (USD/KRW)**
```python
{
    "ticker": "KRW=X",
    "current": 1380.5,
    "history": [...],
    "ma7": 1375.0,
    "ma30": 1360.0,
    "change_pct_week": 0.8,
    "change_pct_month": 2.1
}
```

### 3.2 네이버 DataLab (실제 데이터)

**API**: `https://openapi.naver.com/v1/datalab/search`

**요청 형식**
```json
{
  "startDate": "2024-11-01",
  "endDate": "2024-12-01",
  "timeUnit": "date",
  "keywordGroups": [
    {
      "groupName": "그랜저",
      "keywords": ["그랜저", "그랜저 중고", "그랜저 가격"]
    }
  ]
}
```

**응답 형식**
```json
{
  "results": [
    {
      "title": "그랜저",
      "keywords": ["그랜저", "그랜저 중고", "그랜저 가격"],
      "data": [
        {"period": "2024-11-01", "ratio": 45.2},
        {"period": "2024-11-02", "ratio": 48.7},
        ...
      ]
    }
  ]
}
```

### 3.3 한국은행 (정적 데이터)

**기준금리**
```python
# 정적 데이터 (enhanced_timing.py)
INTEREST_RATE_HISTORY = {
    "current": 3.25,
    "previous": 3.50,
    "last_change": "2024-10-17",
    "direction": "freeze"  # up/down/freeze
}
```

**금통위 일정**
```python
BOK_MEETING_DATES_2024 = [
    "2024-01-11", "2024-02-22", "2024-04-11",
    "2024-05-23", "2024-07-11", "2024-08-22",
    "2024-10-17", "2024-11-28"
]
```

---

## 4. 정적 데이터

### 4.1 신차 출시 일정

**위치**: `new_car_schedule.csv`

```csv
brand,model,release_date,type
현대,그랜저,2024-11-15,풀체인지
기아,쏘렌토,2025-01-20,페이스리프트
BMW,5시리즈,2024-12-01,풀체인지
```

### 4.2 지역별 수요 지수

**위치**: `ml-service/services/enhanced_timing.py` (정적 정의)

```python
REGIONAL_DEMAND_INDEX = {
    '서울': 95,
    '경기': 100,
    '인천': 85,
    '부산': 80,
    '대구': 75,
    '광주': 70,
    '대전': 72,
    '울산': 65,
    '세종': 60,
    '강원': 55,
    '충북': 58,
    '충남': 62,
    '전북': 52,
    '전남': 50,
    '경북': 55,
    '경남': 68,
    '제주': 45
}
```

### 4.3 B2B 차종 데이터

**위치**: `ml-service/services/b2b_intelligence.py`

```python
VEHICLE_DATA = {
    '그랜저 IG': {
        'segment': 'large_sedan',
        'avg_price': 3200,       # 만원
        'depreciation': 0.12,    # 연간 감가율
        'demand_trend': 'stable' # rising/stable/declining
    },
    '쏘렌토 MQ4': {
        'segment': 'mid_suv',
        'avg_price': 3800,
        'depreciation': 0.10,
        'demand_trend': 'rising'
    },
    # ... 10개 차종
}
```

### 4.4 민감도 매트릭스

```python
SENSITIVITY_MATRIX = {
    'large_sedan': {
        'interest_rate': -0.15,   # 금리 1% 인상 시 수요 -15%
        'oil_price': -0.05,       # 유가 10% 인상 시 수요 -5%
        'exchange_rate': -0.03    # 환율 100원 상승 시 수요 -3%
    },
    'ev': {
        'interest_rate': -0.10,
        'oil_price': 0.15,        # EV는 유가 상승 시 수요 증가
        'exchange_rate': -0.05
    },
    # ... 9개 세그먼트
}
```

---

## 5. 시뮬레이션 데이터

> **중요**: 아래 데이터는 실제가 아닌 시뮬레이션입니다.

### 5.1 생성 방식

```python
def _get_deterministic_random(self, seed_str: str, min_val: float, max_val: float):
    """
    일관된 랜덤 값 생성
    - 같은 날짜/모델 조합은 항상 같은 값 반환
    - MD5 해시 기반
    """
    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    normalized = (hash_val % 10000) / 10000
    return min_val + normalized * (max_val - min_val)
```

### 5.2 시뮬레이션 항목

| 항목 | 생성 방식 | 범위 |
|------|----------|------|
| 차종별 ROI | `_get_deterministic_random(f"roi_{model}_{today}")` | -5% ~ 18% |
| 위험도 점수 | `_get_deterministic_random(f"risk_{model}_{today}")` | 10 ~ 90 |
| API 일일 호출량 | `_get_deterministic_random(f"api_{today}")` | 45,000 ~ 65,000 |
| 예측 정확도 | 고정 범위 내 오차 시뮬레이션 | 85% ~ 98% |

---

## 6. 데이터 흐름 다이어그램

### 6.1 가격 예측 데이터 흐름

```
[사용자 입력]
     │
     ▼
{brand, model, year, mileage, fuel, options}
     │
     ▼
[Encoder 변환] ← encoders.pkl
     │
     ▼
{brand_encoded, model_encoded, year, mileage, fuel_encoded, ...}
     │
     ▼
[XGBoost 모델] ← domestic_v12_*.pkl
     │
     ▼
[예측 가격] → [신뢰구간 계산]
     │
     ▼
{predicted_price: 3200, price_range: [2900, 3500], confidence: 0.87}
```

### 6.2 타이밍 분석 데이터 흐름

```
[모델명 입력]
     │
     ├────────────────────────────────────────────┐
     ▼                                            ▼
[Yahoo Finance]                          [네이버 DataLab]
     │                                            │
     ▼                                            ▼
{oil: 72.5, exchange: 1380}             {search_ratio: 45.2}
     │                                            │
     ├────────────────────────────────────────────┤
     ▼                                            ▼
[거시경제 점수] ← 금리/유가/환율        [트렌드 점수] ← 검색량
     │                                            │
     └─────────────────┬──────────────────────────┘
                       ▼
              [신차일정 점수] ← CSV
                       │
                       ▼
              [가중 합산 (40:30:30)]
                       │
                       ▼
              {timing_score: 65, reasons: [...]}
```

---

*이 문서는 실제 코드와 파일을 기반으로 작성되었습니다.*
