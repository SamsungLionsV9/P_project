# AI 도구 활용 및 모델 생성 설명

## 개요

본 프로젝트의 ML 모델 훈련 스크립트는 **Claude Opus** AI 도구의 조언을 받아 구성되었습니다.
도메인 지식(중고차 시장)이 부족한 상태에서 AI의 조언을 통해 핵심 피처 엔지니어링 및 모델 설계를 진행했습니다.

---

## 대상 파일

- `scripts/training/train_domestic_v12_fuel.py` - 국산차 모델 훈련
- `scripts/training/train_imported_v14_fuel.py` - 수입차 모델 훈련

---

## AI 조언 적용 영역

### 1. Target Encoding (핵심 피처 생성)

**AI 조언**: "중고차 가격은 동일 모델+연식+주행거리 조합에서 유사하므로, 단순 Label Encoding보다 Target Encoding이 효과적입니다."

```python
# 국산차 (train_domestic_v12_fuel.py:79-90)
model_enc = df.groupby('Model')['Price'].mean()
model_year_enc = df.groupby('Model_Year')['Price'].mean()
model_year_mg_enc = df.groupby('Model_Year_MG')['Price'].mean()
```

**계층적 Fallback 구조**: `Model_Year_MG` → `Model_Year` → `Model` → `global_mean`

---

### 2. Smooth Encoding (외제차 - 과적합 방지)

**AI 조언**: "외제차는 희소 모델이 많으므로, Bayesian Smoothing을 적용해 데이터 수가 적을 때 전역 평균에 가깝게 조정하세요."

```python
# 외제차 (train_imported_v14_fuel.py:149-152)
def smooth_enc(df, col, target, min_n=30):
    g_mean = df[target].mean()
    stats = df.groupby(col)[target].agg(['mean', 'count'])
    return ((stats['mean'] * stats['count'] + g_mean * min_n) / (stats['count'] + min_n)).to_dict(), g_mean
```

**수식**: `smoothed = (group_mean × count + global_mean × min_n) / (count + min_n)`

---

### 3. Monotone Constraints (단조 제약)

**AI 조언**: "무사고 차량은 항상 더 비싸고, 옵션이 많을수록 가격이 높아야 합니다. XGBoost의 monotone_constraints로 도메인 규칙을 강제하세요."

```python
# 국산차 (train_domestic_v12_fuel.py:131-132)
mono = (0,0,0,0, 0,0,0,0, 0,0,0, 0,0,0, 1,1, 1,1, 1,1,1,1,1,1,1,1)
```

| 값 | 의미 |
|---|---|
| `0` | 제약 없음 (연료, 연식 등) |
| `1` | 양의 관계 강제 (옵션, 무사고, 검사등급) |

---

### 4. 로그 변환 (Log Transform)

**AI 조언**: "중고차 가격은 우측 꼬리 분포이므로 log 변환 후 학습하고, 예측 시 역변환하면 정확도가 올라갑니다."

```python
y_train = np.log1p(train_df['Price'])  # 학습 시 log 변환
pred = np.expm1(model.predict(X_test))  # 예측 후 역변환
```

---

### 5. Z-Score 기반 아웃라이어 제거

**AI 조언**: "동일 모델+연식에서 표준편차 1배 이상 벗어나는 가격은 비정상 데이터일 가능성이 높습니다."

```python
# train_imported_v14_fuel.py:134-135
df['z_score'] = np.abs(df['Base_Price'] - df['mean']) / (df['std'] + 1)
df = df[df['z_score'] <= 1.0].copy()
```

---

### 6. 브랜드/클래스 계층 구조 (외제차)

**AI 조언**: "외제차는 브랜드 등급과 차급(클래스)이 가격에 결정적입니다."

```python
# train_imported_v14_fuel.py:73-80
BRAND_TIER = {
    '페라리': 6, '람보르기니': 6, '맥라렌': 6, '롤스로이스': 6, '벤틀리': 6,
    '포르쉐': 5, '마세라티': 5,
    '벤츠': 4, 'BMW': 4, '아우디': 4, '렉서스': 4, '테슬라': 4,
    ...
}
```

---

### 7. 옵션 프리미엄 분리 (외제차)

**AI 조언**: "고가 옵션은 가격에 큰 영향을 줍니다. 옵션 가치를 분리 계산 후 Base Price만 학습하면 더 정확합니다."

```python
# train_imported_v14_fuel.py:64-71
OPTION_PREMIUM = {
    'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
    'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
    'has_smart_key': 50, 'has_rear_camera': 50,
}
df['Base_Price'] = (df['Price'] - df['Option_Premium']).clip(lower=100)
```

---

## 요약

| 문제 | AI 조언 해결책 |
|------|---------------|
| 범주형 변수 처리 | Target Encoding + 계층적 Fallback |
| 희소 데이터 과적합 | Smooth Encoding (Bayesian Smoothing) |
| 도메인 규칙 위반 | Monotone Constraints |
| 비정상 분포 | Log Transform |
| 이상치 제거 | Z-Score 기반 필터링 |
| 브랜드/차급 영향 | BRAND_TIER, CLASS_RANK 수동 정의 |
| 옵션 가격 분리 | Option Premium 별도 계산 |

---

## 사용 도구

- **Claude Opus**: 도메인 지식 조언 및 피처 엔지니어링 설계
- **Windsurf Cascade**: 코드 구현 및 디버깅
