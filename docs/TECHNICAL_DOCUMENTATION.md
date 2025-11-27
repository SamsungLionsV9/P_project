# Car-Sentix 기술 문서

## 1. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Flutter App (프론트엔드)                       │
│  ├─ Provider 상태관리 (Theme, Comparison, RecentViews, PopularCars)  │
│  └─ SharedPreferences (로컬 캐시)                                    │
└───────────────────────────────────────────────────────────────────────┘
                              │ HTTP API
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ml-service (FastAPI) :8001                       │
│  ├─ PredictionServiceV12 (가격 예측)                                 │
│  ├─ TimingService (구매 타이밍 분석)                                  │
│  ├─ GroqService (AI 대본/분석)                                       │
│  ├─ RecommendationService (추천/이력/즐겨찾기)                        │
│  └─ SimilarService (비슷한 가격 분포)                                 │
└───────────────────────────────────────────────────────────────────────┘
                              │ SQLite
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      data/user_data.db                               │
│  ├─ search_history (검색 이력)                                       │
│  ├─ favorites (즐겨찾기)                                             │
│  ├─ price_alerts (가격 알림)                                         │
│  └─ search_stats (검색 통계)                                         │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. 가격 예측 (PredictionServiceV12)

### 2.1 모델 구조
- **국산차**: `domestic_v12.pkl` (MAPE 9.7%)
- **외제차**: `imported_v14.pkl` (MAPE 12.0%)
- **알고리즘**: LightGBM (Gradient Boosting)

### 2.2 피처 (Features)

| 피처명 | 설명 | 데이터 출처 |
|--------|------|-------------|
| Model_enc | 모델별 평균 가격 인코딩 | 엔카 크롤링 데이터 |
| Model_Year_enc | 모델+연식 조합 인코딩 | 엔카 크롤링 데이터 |
| Model_Year_MG_enc | 모델+연식+주행거리그룹 | 엔카 크롤링 데이터 |
| Age, Age_log, Age_sq | 차량 나이 (비선형 포함) | 계산값 |
| Mileage, Mile_log | 주행거리 | 사용자 입력 |
| Km_per_Year | 연간 평균 주행거리 | 계산값 |
| Fuel_enc | 연료 타입 인코딩 | 엔카 크롤링 데이터 |
| is_diesel, is_hybrid, is_lpg | 연료 원핫 인코딩 | 사용자 입력 |
| Opt_Count | 옵션 개수 | 사용자 입력 |
| Opt_Premium | 옵션 프리미엄 점수 | 계산값 |

### 2.3 연료 타입 조정 계수
```python
FUEL_ADJUSTMENT = {
    '가솔린': 1.0,      # 기준
    '디젤': 0.98,       # 2% 할인 (국산차)
    '하이브리드': 1.08,  # 8% 프리미엄
    'LPG': 0.92         # 8% 할인
}
```

---

## 3. 상세 옵션 및 성능 점검

### 3.1 옵션 프리미엄 계산 (국산차)
```python
opt_premium = (
    has_sunroof * 3 +           # 선루프: +3점
    has_leather_seat * 2 +      # 가죽시트: +2점
    has_ventilated_seat * 3 +   # 통풍시트: +3점
    has_led_lamp * 2            # LED 램프: +2점
)
```

### 3.2 옵션 프리미엄 계산 (외제차)
```python
IMPORTED_OPT_PREMIUM = {
    'has_ventilated_seat': 120,  # 통풍시트: +120만원
    'has_sunroof': 100,          # 선루프: +100만원
    'has_led_lamp': 100,         # LED: +100만원
    'has_leather_seat': 80,      # 가죽시트: +80만원
    'has_navigation': 80,        # 내비게이션: +80만원
    'has_heated_seat': 60,       # 열선시트: +60만원
    'has_smart_key': 50,         # 스마트키: +50만원
    'has_rear_camera': 50,       # 후방카메라: +50만원
}
```

### 3.3 성능 점검 등급
```python
grade_map = {
    'normal': 0,     # 보통 (별 1-2개)
    'good': 1,       # 양호 (별 3-4개)
    'excellent': 2   # 우수 (별 5개)
}
```

### 3.4 데이터 출처
- **학습 데이터**: 엔카(encar.com) 크롤링 데이터
- **데이터 기간**: 최근 3년 매물 데이터
- **데이터량**: 국산차 ~30만건, 외제차 ~10만건

---

## 4. 신뢰도 및 가격 분포 계산

### 4.1 신뢰도(Confidence) 계산
```python
# 기본 공식: MAPE가 낮을수록 신뢰도 높음
confidence = max(50, min(98, 95 - (MAPE - 5) * 2))

# 예시: MAPE 9.7%인 경우
# confidence = 95 - (9.7 - 5) * 2 = 95 - 9.4 = 85.6%

# 추가 불확실성 요소
opt_uncertainty = opt_count * 0.5      # 옵션당 +0.5%
fuel_uncertainty = {
    '하이브리드': 1.5,  # 하이브리드 +1.5%
    'LPG': 2.0,         # LPG +2.0%
    '디젤': 0.5         # 디젤 +0.5%
}.get(fuel, 0)

total_uncertainty = MAPE + opt_uncertainty + fuel_uncertainty
```

### 4.2 가격 범위(Price Range) 계산
```python
error_margin = predicted_price * (total_uncertainty / 100)
price_range = (
    predicted_price - error_margin,  # 하한
    predicted_price + error_margin   # 상한
)
```

### 4.3 비슷한 차량 가격 분포
```python
# 1. 비슷한 차량 필터링
similar = df[
    (brand 일치) &
    (model_name 포함) &
    (연식 ±2년) &
    (주행거리 ±30,000km)
]

# 2. 이상치 제거 (IQR 방법)
q1, q3 = np.percentile(prices, [25, 75])
iqr = q3 - q1
lower_bound = max(q1 - 1.5 * iqr, 100)   # 최소 100만원
upper_bound = min(q3 + 1.5 * iqr, 10000) # 최대 1억

# 3. 분포 통계
distribution = {
    'min': 최저가,
    'q1': 하위 25%,
    'median': 중앙값,
    'q3': 상위 25%,
    'max': 최고가,
    'mean': 평균,
    'std': 표준편차
}
```

### 4.4 신뢰도 의미
| 신뢰도 | 의미 | MAPE |
|--------|------|------|
| 90%+ | 매우 정확 | < 7.5% |
| 85-90% | 정확 | 7.5-10% |
| 80-85% | 보통 | 10-12.5% |
| 75-80% | 참고용 | 12.5-15% |
| < 75% | 불확실 | > 15% |

---

## 5. 구매 타이밍 분석

### 5.1 타이밍 점수 구성
```python
timing_score = (
    seasonal_score * 0.3 +     # 계절성 (30%)
    market_trend * 0.3 +       # 시장 추세 (30%)
    model_lifecycle * 0.2 +    # 신차 출시 주기 (20%)
    demand_supply * 0.2        # 수요/공급 (20%)
)
```

### 5.2 판정 기준
| 점수 | 판정 | 의미 |
|------|------|------|
| 70+ | 매수 | 지금 구매 추천 |
| 55-70 | 관망 | 조금 더 기다려 보세요 |
| < 55 | 회피 | 구매 보류 권장 |

---

## 6. Groq AI 대본 생성

### 6.1 호출 흐름
```
1. Flutter App에서 /api/negotiation/generate 호출
2. run_server.py에서 Groq 서비스 호출
3. groq_advisor.py에서 프롬프트 생성 및 API 호출
4. Groq API (llama-3.3-70b-versatile) 응답
5. JSON 파싱 후 Flutter에 반환
```

### 6.2 프롬프트 구조
```python
prompt = f"""
📊 상황:
- 차량: {brand} {model}
- 판매가: {sale_price:,}만원
- AI 예측가: {predicted_price:,.0f}만원
- 목표 가격: {target_price:,}만원

⚠️ 발견된 문제점:
{issues}

🎯 협상 스타일: {style}

JSON 형식으로 반환:
- message_script: 문자 메시지 초안
- phone_script: 전화 통화 대본
- key_arguments: 핵심 논거
- negotiation_tips: 협상 팁
"""
```

### 6.3 Fallback 처리
Groq API 실패 시 템플릿 기반 대본 생성:
```python
message_script = f"안녕하세요. {model} 매물 관심있어서 연락드립니다. 
빅데이터 분석 결과 적정가가 {target_price:,}만원으로 나왔는데, 
{target_price:,}만원에 거래 가능할까요?"
```

---

## 7. 모델명 매핑 (Frontend → Backend)

### 7.1 현대
| UI 표시 | 연식 | Backend 모델명 |
|---------|------|----------------|
| 그랜저 | 2023+ | 그랜저 (GN7) |
| 그랜저 | 2020-2022 | 더 뉴 그랜저 IG |
| 그랜저 | 2017-2019 | 그랜저 IG |
| 그랜저 | ~2016 | 그랜저 HG |

### 7.2 기아
| UI 표시 | 연식 | Backend 모델명 |
|---------|------|----------------|
| K9 | 2022+ | 더 뉴 K9 2세대 |
| K9 | 2018-2021 | 더 K9 |
| K9 | ~2017 | K9 |
| K5 | 2024+ | 더 뉴 K5 (DL3) |
| K5 | 2020-2023 | K5 (DL3) |

---

## 8. API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /api/predict | 가격 예측 |
| POST | /api/smart-analysis | 통합 분석 |
| POST | /api/similar | 비슷한 가격 분포 |
| POST | /api/timing | 구매 타이밍 |
| POST | /api/negotiation/generate | AI 네고 대본 |
| GET | /api/popular | 인기 모델 |
| GET | /api/recommendations | 추천 차량 |
| GET | /api/history | 검색 이력 |
| DELETE | /api/history/{id} | 이력 삭제 |
| POST | /api/favorites | 즐겨찾기 추가 |
| DELETE | /api/favorites/{id} | 즐겨찾기 삭제 |

---

*최종 업데이트: 2025.11.27*
