# ML 모델 명세서

## 개요

중고차 가격 예측을 위해 XGBoost 기반 회귀 모델을 사용합니다. 국내차와 수입차는 가격 형성 요인이 다르므로 별도 모델로 학습되었습니다.

---

## 모델 구성

| 모델 | 버전 | 대상 | 학습 데이터 | MAPE |
|------|------|------|-------------|------|
| Domestic | v12 | 국내차 | 엔카 15,000+ 건 | 9.8% |
| Imported | v14 | 수입차 | 엔카 8,000+ 건 | 11.2% |

---

## 국내차 모델 (v12)

### 지원 브랜드

```
현대, 기아, 제네시스, 쉐보레, 르노코리아, KG모빌리티
```

### 입력 피처

| 피처 | 타입 | 설명 |
|------|------|------|
| `brand` | Categorical | 제조사 |
| `model` | Categorical | 모델명 |
| `year` | Numeric | 연식 (예: 2020) |
| `mileage` | Numeric | 주행거리 (km) |
| `fuel` | Categorical | 연료 (가솔린/디젤/하이브리드/LPG/전기) |
| `accident_free` | Boolean | 무사고 여부 |
| `options` | Dict | 옵션 (선루프, 네비 등) |

### 연료별 가격 조정 계수

| 연료 | 조정 계수 | 설명 |
|------|----------|------|
| 가솔린 | 1.00 | 기준 |
| 디젤 | 0.97 | -3% |
| 하이브리드 | 1.05 | +5% |
| LPG | 0.90 | -10% |
| 전기 | 1.08 | +8% |

### 모델 파일

```
models/
├── domestic_v12.pkl           # XGBoost 모델
├── domestic_v12_encoders.pkl  # Label Encoders
└── domestic_v12_features.pkl  # 피처 목록
```

---

## 수입차 모델 (v14)

### 지원 브랜드

```
BMW, 벤츠, 아우디, 폭스바겐, 볼보, 렉서스, 토요타, 혼다, 포르쉐, 
미니, 랜드로버, 재규어, 포드, 지프, 마세라티, 페라리, 람보르기니
```

### 입력 피처

| 피처 | 타입 | 설명 |
|------|------|------|
| `brand` | Categorical | 제조사 |
| `model` | Categorical | 모델명 |
| `year` | Numeric | 연식 |
| `mileage` | Numeric | 주행거리 (km) |
| `fuel` | Categorical | 연료 |
| `accident_free` | Boolean | 무사고 여부 |

### 연료별 가격 조정 계수

| 연료 | 조정 계수 |
|------|----------|
| 가솔린 | 1.00 |
| 디젤 | 0.95 |
| 하이브리드 | 1.08 |
| 전기 | 1.12 |

---

## 예측 파이프라인

```python
def predict(brand, model, year, mileage, fuel, options):
    # 1. 국내차/수입차 분류
    is_domestic = brand in DOMESTIC_BRANDS
    
    # 2. 데이터 전처리
    features = preprocess(brand, model, year, mileage, options)
    
    # 3. 모델 예측 (가솔린 기준)
    if is_domestic:
        base_price = domestic_model.predict(features)
    else:
        base_price = imported_model.predict(features)
    
    # 4. 연료 조정
    fuel_factor = FUEL_ADJUSTMENT[fuel]
    predicted_price = base_price * fuel_factor
    
    # 5. 신뢰도 계산
    confidence = calculate_confidence(features)
    
    # 6. 가격 범위 계산 (±10%)
    price_range = {
        "min": predicted_price * 0.90,
        "max": predicted_price * 1.10
    }
    
    return predicted_price, confidence, price_range
```

---

## 성능 지표

### 국내차 모델 (v12)

| 지표 | 값 |
|------|-----|
| MAPE | 9.8% |
| RMSE | 2,150,000원 |
| R² | 0.92 |
| 학습 데이터 | 15,247건 |
| 테스트 데이터 | 3,812건 |

### 수입차 모델 (v14)

| 지표 | 값 |
|------|-----|
| MAPE | 11.2% |
| RMSE | 3,850,000원 |
| R² | 0.89 |
| 학습 데이터 | 8,134건 |
| 테스트 데이터 | 2,034건 |

---

## 주요 영향 요인

### 가격에 가장 큰 영향을 미치는 요인

| 순위 | 요인 | 중요도 |
|------|------|--------|
| 1 | 연식 | 35% |
| 2 | 모델 | 25% |
| 3 | 주행거리 | 20% |
| 4 | 브랜드 | 12% |
| 5 | 옵션/사고여부 | 8% |

### 감가상각 패턴

```
Year 1: -15~20%
Year 2: -10~15%
Year 3: -8~12%
Year 4+: -5~8% (연간)
```

---

## 한계점 및 주의사항

1. **데이터 범위**: 엔카 매물 기준으로 학습되어, 극단적인 가격대는 예측 정확도가 낮을 수 있음
2. **신모델**: 출시 1년 미만 신모델은 학습 데이터 부족으로 예측 정확도 저하
3. **옵션 반영**: 세부 옵션(색상, 시트 재질 등)은 현재 모델에서 미반영
4. **지역차**: 지역별 가격 차이는 미반영

---

## 향후 개선 계획

- [ ] 실시간 시세 반영을 위한 모델 자동 업데이트
- [ ] 옵션별 세부 가격 영향도 분석
- [ ] 지역별 가격 차이 반영
- [ ] 딥러닝 모델 도입 검토

---

*Last Updated: 2025-11-26*
