# 예측가 계산 로직 상세 문서

## 개요

본 서비스에서 예측가는 **두 가지 다른 컨텍스트**에서 계산됩니다:

1. **결과 페이지 예측가**: 사용자가 입력한 조건으로 계산
2. **개별 매물 예측가**: 각 매물의 실제 조건으로 계산

---

## 1. 예측가 계산 공식

### 기본 공식

```
예측가 = ML_기본가(브랜드, 모델, 연식, 주행거리, 연료) + 옵션_프리미엄
```

### ML 모델 예측 (`prediction_v12.py`)

```python
def predict(self, brand: str, model: str, year: int, mileage: int, fuel: str = '가솔린') -> PredictionResult:
    # 1. 입력 데이터 전처리
    model_normalized = normalize_model_name(model)
    fuel_normalized = normalize_fuel_type(fuel)
    
    # 2. 특성 벡터 생성
    features = {
        'Model': model_normalized,
        'YearOnly': year,
        'Mileage': mileage,
        'FuelType': fuel_normalized,
        # 옵션 특성들 (있으면 반영)
        'Sunroof': sunroof,
        'Navigation': navigation,
        'Leather': leather,
        ...
    }
    
    # 3. 모델 예측
    predicted_price = model.predict(features)
    
    return PredictionResult(
        predicted_price=predicted_price,
        price_range=(lower_bound, upper_bound),
        confidence=confidence_score
    )
```

### 옵션 프리미엄 계산

```python
OPTION_PREMIUM = {
    'sunroof': 60,      # 선루프: +60만원
    'navigation': 30,   # 내비게이션: +30만원
    'leather': 50,      # 가죽시트: +50만원
    'heated_seat': 20,  # 열선시트: +20만원
    'ventilated_seat': 30,  # 통풍시트: +30만원
    'hud': 40,          # 헤드업디스플레이: +40만원
    'around_view': 35,  # 어라운드뷰: +35만원
    'smart_cruise': 25, # 스마트크루즈: +25만원
}

def calculate_option_premium(options: Dict) -> int:
    """옵션에 따른 프리미엄 계산"""
    premium = 0
    for option, value in options.items():
        if value and option in OPTION_PREMIUM:
            premium += OPTION_PREMIUM[option]
    return premium
```

---

## 2. 결과 페이지 예측가 vs 개별 매물 예측가

### 2.1 결과 페이지 예측가

**사용자가 입력한 조건**으로 계산됩니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│  [사용자 입력]                                                       │
│  브랜드: 현대                                                        │
│  모델: 그랜저                                                        │
│  연식: 2025년                                                        │
│  주행거리: 10,000km                                                  │
│  연료: 가솔린                                                        │
│  옵션: 선루프 ✓, 내비 ✓                                              │
│                                                                      │
│  [계산]                                                              │
│  ML_기본가(현대, 그랜저, 2025, 10000, 가솔린) = 3,058만원            │
│  옵션_프리미엄(선루프+내비) = 60 + 30 = 90만원                       │
│                                                                      │
│  [결과]                                                              │
│  예측가 = 3,058 + 90 = 3,148만원                                    │
└─────────────────────────────────────────────────────────────────────┘
```

**코드 흐름**:

```
car_info_input_page.dart
    ↓
run_server.py → /api/predict
    ↓
prediction_v12.py → predict()
    ↓
결과: 3,148만원
```

### 2.2 개별 매물 예측가

**각 매물의 실제 조건**으로 개별 계산됩니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│  [매물 1: 실제가 3,310만원]                                          │
│  연식: 2025년                                                        │
│  주행거리: 341km (거의 신차)                                         │
│  연료: 가솔린                                                        │
│  옵션: 선루프 ✓, 내비 ✓, 가죽 ✓                                      │
│                                                                      │
│  [계산]                                                              │
│  ML_기본가(현대, 그랜저, 2025, 341, 가솔린) = 3,343만원              │
│  → 주행거리 341km = 사실상 신차급, 더 높은 가격                      │
│  옵션_프리미엄(선루프+내비+가죽) = 60 + 30 + 50 = 140만원            │
│                                                                      │
│  [결과]                                                              │
│  예측가 = 3,343 + 140 = 3,483만원                                   │
│  차이 = 3,483 - 3,310 = +173만원 (저렴!)                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  [매물 2: 실제가 4,190만원]                                          │
│  연식: 2025년                                                        │
│  주행거리: 9,637km                                                   │
│  연료: 가솔린                                                        │
│  옵션: 무사고 ✓, 선루프 ✓, 내비 ✓                                    │
│                                                                      │
│  [계산]                                                              │
│  ML_기본가(현대, 그랜저, 2025, 9637, 가솔린) = 3,627만원             │
│  옵션_프리미엄(선루프+내비) = 60 + 30 = 90만원                       │
│  무사고_프리미엄 = 별도 계산 (성능점검등급 반영)                      │
│                                                                      │
│  [결과]                                                              │
│  예측가 = 3,627 + 90 = 3,717만원                                    │
│  차이 = 3,717 - 4,190 = -473만원 (비쌈!)                            │
└─────────────────────────────────────────────────────────────────────┘
```

**코드 흐름**:

```
recommendation_service.py → get_model_deals()
    ↓
for each deal in deals:
    prediction_v12.py → predict(deal.year, deal.mileage, deal.fuel)
    ↓
    개별 예측가 계산
    ↓
result_page.dart → 매물별 예측가 표시
```

---

## 3. 예측가가 다른 이유

### 3.1 주행거리 차이

```
┌────────────────┬────────────────┬────────────────┐
│ 주행거리        │ ML 모델 반영    │ 예측가 영향     │
├────────────────┼────────────────┼────────────────┤
│ 341km (신차급) │ 감가 거의 없음  │ +300~500만원   │
│ 10,000km       │ 정상 감가       │ 기준가         │
│ 30,000km       │ 큰 감가         │ -200~400만원   │
└────────────────┴────────────────┴────────────────┘
```

**ML 모델 내부 로직**:
```python
# 주행거리별 가격 감가율 (대략적 예시)
def mileage_depreciation(mileage: int, base_price: int) -> int:
    if mileage < 1000:
        return base_price * 0.98  # 신차급: 2% 감가
    elif mileage < 10000:
        return base_price * 0.95  # 1만km 이하: 5% 감가
    elif mileage < 30000:
        return base_price * 0.88  # 3만km 이하: 12% 감가
    else:
        return base_price * 0.80  # 3만km 초과: 20% 감가
```

### 3.2 옵션 차이

```
┌─────────────────────────────────────────────────────────────────────┐
│  사용자 입력 (결과 페이지)     │  매물 1               │  매물 2    │
├───────────────────────────────┼───────────────────────┼────────────┤
│  선루프: ✓ (+60)              │  선루프: ✓ (+60)      │  선루프: ✓ │
│  내비: ✓ (+30)                │  내비: ✓ (+30)        │  내비: ✓   │
│  가죽: ✗                       │  가죽: ✓ (+50)        │  가죽: ✗   │
│  무사고: ✗                     │  무사고: ✗            │  무사고: ✓ │
├───────────────────────────────┼───────────────────────┼────────────┤
│  옵션 프리미엄: 90만원         │  옵션 프리미엄: 140만원│  90만원+α  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 연료 타입 차이

```
┌────────────┬────────────────────────────────────────┐
│ 연료 타입   │ 가격 영향                              │
├────────────┼────────────────────────────────────────┤
│ 가솔린      │ 기준가                                 │
│ 디젤        │ +100~200만원 (연비 우수)               │
│ 하이브리드  │ +200~400만원 (친환경)                  │
│ LPG        │ -100~200만원 (유지비 저렴, 인기 낮음)  │
└────────────┴────────────────────────────────────────┘
```

---

## 4. 코드 상세

### 4.1 결과 페이지 API 호출 (`run_server.py`)

```python
@app.post("/api/predict")
async def predict(request: PredictRequest):
    # 사용자 입력 조건으로 예측
    result = prediction_service.predict(
        brand=request.brand,
        model=request.model,
        year=request.year,
        mileage=request.mileage,
        fuel=request.fuel,
        options=request.options  # 사용자 선택 옵션
    )
    
    return {
        "prediction": {
            "predicted_price": result.predicted_price,
            "price_range": result.price_range,
            "confidence": result.confidence
        }
    }
```

### 4.2 개별 매물 예측 (`recommendation_service.py`)

```python
def get_model_deals(self, brand: str, model: str, limit: int = 10) -> List[Dict]:
    """특정 모델의 가성비 좋은 매물 추천"""
    
    for _, row in df.iterrows():
        # 각 매물의 실제 조건 추출
        car_id = row.get('Id', '')
        year = int(row.get('YearOnly', 2020))
        mileage = int(row.get('Mileage', 50000))  # 실제 주행거리
        actual_price = int(row.get('Price', 0))   # 실제 판매가
        fuel = str(row.get('FuelType', '가솔린'))
        
        # 해당 매물 조건으로 예측가 계산
        if self._prediction_service:
            result = self._prediction_service.predict(
                brand, model, year, mileage, fuel=fuel
            )
            predicted_price = result.predicted_price
        
        # 옵션 정보 조회 (DB에서)
        options = self.get_car_options(car_id)
        
        deals.append({
            'car_id': car_id,
            'year': year,
            'mileage': mileage,
            'actual_price': actual_price,
            'predicted_price': predicted_price,  # 개별 예측가
            'price_diff': predicted_price - actual_price,
            'options': options
        })
    
    return deals
```

### 4.3 옵션 정보 조회 (`recommendation_service.py`)

```python
def get_car_options(self, car_id: str) -> Dict:
    """차량 ID로 옵션 정보 조회"""
    if not car_id or self._details_df is None:
        return None
    
    match = self._details_df[self._details_df['car_id'] == car_id]
    if len(match) == 0:
        return None
    
    row = match.iloc[0]
    return {
        'sunroof': bool(row.get('Sunroof', False)),
        'navigation': bool(row.get('Navigation', False)),
        'leather': bool(row.get('Leather', False)),
        'heated_seat': bool(row.get('HeatedSeat', False)),
        'ventilated_seat': bool(row.get('VentilatedSeat', False)),
        'smart_cruise': bool(row.get('SmartCruise', False)),
        'hud': bool(row.get('HUD', False)),
        'around_view': bool(row.get('AroundView', False)),
        'accident_free': bool(row.get('AccidentFree', False)),
    }
```

---

## 5. 예시 비교

### 현대 그랜저 2025년식 비교

| 구분 | 사용자 입력 | 매물 1 | 매물 2 |
|------|------------|--------|--------|
| **주행거리** | 10,000km | 341km | 9,637km |
| **연료** | 가솔린 | 가솔린 | 가솔린 |
| **옵션** | 선루프+내비 | 선루프+내비+가죽 | 무사고+선루프+내비 |
| **ML 기본가** | 3,058만원 | 3,343만원 | 3,627만원 |
| **옵션 프리미엄** | +90만원 | +140만원 | +90만원 |
| **예측가** | **3,148만원** | **3,483만원** | **3,717만원** |
| **실제가** | - | 3,310만원 | 4,190만원 |
| **판정** | - | ✅ 저렴 (+173) | ❌ 비쌈 (-473) |

### 왜 예측가가 다른가?

```
매물 1 (3,483만원) > 사용자 입력 (3,148만원)
─────────────────────────────────────────
이유 1: 주행거리 341km << 10,000km → +약 285만원
이유 2: 가죽시트 옵션 추가 → +50만원

매물 2 (3,717만원) > 매물 1 (3,483만원)
─────────────────────────────────────────
이유 1: 주행거리 9,637km > 341km → +약 284만원
이유 2: 가죽시트 없음 → -50만원
이유 3: 무사고 프리미엄 → +약 50만원
```

---

## 6. 정리

| 예측가 유형 | 계산 조건 | 사용 위치 |
|------------|----------|----------|
| 결과 페이지 예측가 | 사용자 입력 조건 | 메인 결과 화면 상단 |
| 개별 매물 예측가 | 각 매물의 실제 조건 | 매물 카드, 상세 모달 |

**핵심 차이점**:
- 주행거리가 다르면 예측가도 다름
- 옵션이 다르면 프리미엄이 다름
- 연료 타입이 다르면 기본가가 다름
- **같은 모델이라도 조건이 다르면 예측가는 항상 다름**
