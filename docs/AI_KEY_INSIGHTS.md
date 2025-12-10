# Claude Opus 핵심 조언 TOP 3

> 본 문서는 중고차 가격 예측 모델 개발 시 Claude Opus로부터 받은 **가장 핵심적인 3가지 조언**을 정리한 것입니다.

---

## 🥇 1. Target Encoding + 계층적 Fallback

### 문제 상황
- 중고차 모델명은 수천 가지 (고차원 범주형 변수)
- One-Hot Encoding → 차원 폭발
- Label Encoding → 의미 없는 숫자 부여

### AI 조언
> "중고차 가격은 **동일 모델+연식+주행거리 그룹**에서 매우 유사합니다. 
> 각 그룹의 **평균 가격을 피처로 사용**하세요 (Target Encoding).
> 데이터가 부족한 그룹은 **상위 계층 평균으로 Fallback**하면 됩니다."

### 적용 코드
```python
# 계층 구조: Model_Year_MG → Model_Year → Model → global_mean
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc) \
                          .fillna(df['Model_Year_enc'])  # Fallback
```

### 효과
- 희소 데이터에도 안정적인 예측
- 모델이 "그랜저 2022년 3만km"의 시세를 직접 학습

---

## 🥈 2. Monotone Constraints (도메인 규칙 강제)

### 문제 상황
- ML 모델이 "옵션이 많을수록 가격이 낮다"고 잘못 학습하는 경우 발생
- 데이터 노이즈로 인한 비상식적 결과

### AI 조언
> "중고차 시장에서 **절대 위반되면 안 되는 규칙**이 있습니다:
> 1. 무사고 차량 ≥ 사고 차량
> 2. 옵션 多 ≥ 옵션 少
> 3. 검사등급 高 ≥ 검사등급 低
> 
> XGBoost의 `monotone_constraints`로 이 규칙을 **강제**하세요."

### 적용 코드
```python
# 1 = 양의 관계 강제, 0 = 제약 없음
mono = (0,0,0,0,  # 인코딩 피처 (제약 없음)
        0,0,0,    # 연료 (제약 없음)
        0,0,0,    # 연식/주행 (제약 없음)
        1,1,      # is_accident_free, inspection_grade (양의 관계)
        1,1,1,1,1,1,1,1)  # 옵션들 (양의 관계)

model = xgb.XGBRegressor(monotone_constraints=mono, ...)
```

### 효과
- 도메인 상식에 부합하는 예측 결과
- 사용자 신뢰도 향상 (썬루프 있는 차가 더 비싸게 나옴)

---

## 🥉 3. 옵션 프리미엄 분리 학습 (외제차)

### 문제 상황
- 외제차 고가 옵션(통풍시트, 썬루프)은 수백만원 가치
- 동일 모델도 옵션 유무에 따라 가격 차이가 큼
- 모델이 옵션 효과를 제대로 학습하지 못함

### AI 조언
> "**옵션 가치를 미리 계산**해서 가격에서 빼고, **Base Price만 학습**시키세요.
> 예측 시 다시 옵션 가치를 더하면 됩니다.
> 이렇게 하면 모델은 차량 본연의 가치만 학습하게 됩니다."

### 적용 코드
```python
# 옵션별 프리미엄 (만원)
OPTION_PREMIUM = {
    'has_ventilated_seat': 120,  # 통풍시트 120만원
    'has_sunroof': 100,          # 썬루프 100만원
    'has_led_lamp': 100,         # LED램프 100만원
    'has_leather_seat': 80,      # 가죽시트 80만원
    ...
}

# 학습 시: Base Price = 실제가격 - 옵션가치
df['Base_Price'] = df['Price'] - df['Option_Premium']

# 예측 시: 최종가격 = 예측 Base Price + 옵션가치
pred_final = pred_base + option_premium
```

### 효과
- 옵션 효과가 명확하게 분리됨
- "통풍시트 추가하면 얼마나 올라가나요?" 질문에 정확한 답변 가능

---

## 요약

| 순위 | 조언 | 해결한 문제 |
|:---:|------|------------|
| 🥇 | Target Encoding + Fallback | 고차원 범주형 변수 처리 |
| 🥈 | Monotone Constraints | 도메인 규칙 위반 방지 |
| 🥉 | 옵션 프리미엄 분리 | 옵션 가치 정확한 반영 |

---

*작성일: 2025-12-10*
*AI 도구: Claude Opus (Anthropic)*
