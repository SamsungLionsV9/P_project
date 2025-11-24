# 중고차 가격 예측 모델 개선 방안

## 📋 현재 문제점 요약

1. **데이터 품질 이슈**
   - 9999만원 이상치 존재 (플레이스홀더 값)
   - 고가 차량 심각한 과소평가 (평균 4527만원 오차)
   
2. **모델 성능**
   - R² = 0.60 (개선 여지 40%)
   - 가격대별 불균형 (고가: MAPE 22.5%)
   
3. **피처 부족**
   - 현재 5개 피처만 사용
   - 중요 정보 누락 (배기량, 옵션, 등급, 색상 등)

---

## 🎯 단계별 개선 방안

### Phase 1: 데이터 품질 개선 (즉시)

#### 1.1 추가 이상치 제거
```python
# 9999 같은 플레이스홀더 값 제거
df = df[df['price'] < 9000].copy()  # 9000만원 = 9억원 미만
```

#### 1.2 가격대별 층화 샘플링
```python
# 고가 차량 샘플 증가로 학습 강화
from sklearn.model_selection import train_test_split
# stratify 사용하여 가격 구간별 균형 유지
```

---

### Phase 2: 피처 엔지니어링 (중요도 높음)

#### 2.1 기존 피처에서 파생 피처 생성
```python
# 주행거리 관련
df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)

# 차량 나이 구간
df['age_group'] = pd.cut(df['age'], bins=[0, 1, 3, 5, 10, 20], 
                          labels=['신차급', '준신차', '중고', '노후', '고령'])

# 브랜드-연료 조합 (프리미엄 전기차 등)
df['brand_fuel'] = df['brand'] + '_' + df['fuel']

# 모델별 인기도 (같은 모델 데이터 수)
model_counts = df['model_name'].value_counts()
df['model_popularity'] = df['model_name'].map(model_counts)

# 가격 구간 (타겟 누수 주의 - 테스트에선 제외)
# 훈련 시만 사용하는 보조 피처로 활용 가능
```

#### 2.2 상호작용 피처
```python
# 프리미엄 브랜드 여부
premium_brands = ['제네시스', '벤츠', 'BMW', '아우디', '렉서스']
df['is_premium'] = df['brand'].isin(premium_brands).astype(int)

# 프리미엄 × 나이
df['premium_age'] = df['is_premium'] * df['age']

# 브랜드별 주행거리 정규화
brand_mileage_mean = df.groupby('brand')['mileage'].transform('mean')
df['mileage_vs_brand_avg'] = df['mileage'] / brand_mileage_mean
```

#### 2.3 원본 데이터에서 추가 수집 (스크래핑 개선)
- **엔진 정보**: 배기량, 마력, 토크
- **차량 등급**: 트림 레벨 (베이직, 프리미엄, 익스클루시브 등)
- **옵션**: 선루프, 네비게이션, 가죽시트 개수
- **색상**: 인기 색상 여부 (흰색, 검정, 회색 등)
- **사고 이력**: 무사고 여부
- **연식 상세**: 출고 월
- **변속기**: 자동/수동
- **구동방식**: FF/FR/4WD

---

### Phase 3: 모델 개선

#### 3.1 가격대별 모델 앙상블
```python
# 저가/중가/고가 각각 다른 모델 학습
low_price_model = XGBRegressor(...)  # <2000
mid_price_model = XGBRegressor(...)  # 2000-5000
high_price_model = XGBRegressor(...) # 5000+

# 예측 시 가격 범위 추정 후 적절한 모델 선택
```

#### 3.2 더 강력한 하이퍼파라미터 튜닝
```python
# RandomizedSearch 대신 Optuna 사용
import optuna

def objective(trial):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 500, 3000),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0, 1),
        'subsample': trial.suggest_float('subsample', 0.5, 1),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 1)
    }
    # ... 학습 및 평가
```

#### 3.3 모델 앙상블
```python
from sklearn.ensemble import StackingRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# 여러 모델 조합
estimators = [
    ('xgb', XGBRegressor(...)),
    ('lgb', LGBMRegressor(...)),
    ('cat', CatBoostRegressor(...))
]

stacking = StackingRegressor(
    estimators=estimators,
    final_estimator=XGBRegressor(...)
)
```

#### 3.4 가중치 손실 함수
```python
# 고가 차량의 오차에 더 큰 패널티
def weighted_mae(y_true, y_pred):
    weights = np.where(y_true > 5000, 2.0, 1.0)  # 고가는 2배 가중치
    return np.mean(weights * np.abs(y_true - y_pred))
```

---

### Phase 4: 로그 변환 재검토

#### 4.1 현재 문제
- 로그 변환이 고가 차량을 압축시킴
- 역변환 시 오차 증폭

#### 4.2 대안
```python
# 1. Box-Cox 변환 시도
from scipy.stats import boxcox
transformed, lambda_param = boxcox(df['price'] + 1)

# 2. 제곱근 변환 (로그보다 완만)
df['sqrt_price'] = np.sqrt(df['price'])

# 3. 가격대별 다른 변환
# 저가: 로그, 고가: 원본 또는 제곱근
```

---

### Phase 5: 평가 지표 개선

#### 5.1 다중 지표 추적
```python
from sklearn.metrics import mean_absolute_percentage_error

# MAPE (Mean Absolute Percentage Error)
mape = mean_absolute_percentage_error(y_true, y_pred)

# 가격대별 R2
for price_range in ranges:
    mask = (y_true >= low) & (y_true < high)
    r2_range = r2_score(y_true[mask], y_pred[mask])
    print(f"{range_name} R2: {r2_range:.3f}")
```

#### 5.2 비즈니스 지표
```python
# 10% 이내 정확도
accuracy_10pct = (np.abs(percent_error) <= 10).mean()
print(f"10% 이내 정확도: {accuracy_10pct:.2%}")

# 20% 이내 정확도
accuracy_20pct = (np.abs(percent_error) <= 20).mean()
print(f"20% 이내 정확도: {accuracy_20pct:.2%}")
```

---

## 🚀 우선순위 로드맵

### 즉시 적용 (1-2일)
1. ✅ 9999만원 이상치 제거
2. ✅ 기본 파생 피처 추가 (mileage_per_year, age_group 등)
3. ✅ 고가 차량 가중치 적용

**예상 개선**: R² 0.60 → 0.65

### 단기 개선 (1주)
4. ✅ 상호작용 피처 추가
5. ✅ Optuna 하이퍼파라미터 튜닝
6. ✅ 가격대별 성능 모니터링

**예상 개선**: R² 0.65 → 0.70

### 중기 개선 (2-4주)
7. ⬜ 원본 데이터 재수집 (추가 피처)
8. ⬜ LightGBM, CatBoost 실험
9. ⬜ 모델 앙상블

**예상 개선**: R² 0.70 → 0.75+

### 장기 개선 (1-3개월)
10. ⬜ 딥러닝 모델 실험 (TabNet 등)
11. ⬜ 시계열 피처 (계절성, 트렌드)
12. ⬜ 외부 데이터 통합 (경제 지표, 유가 등)

**목표**: R² 0.80+ (세계 최고 수준)

---

## 📈 성공 기준

### 최소 목표
- R² ≥ 0.70
- 전체 MAPE ≤ 12%
- 고가 차량 MAPE ≤ 15%

### 이상적 목표
- R² ≥ 0.75
- 전체 MAPE ≤ 10%
- 모든 가격대 MAPE ≤ 12%
- 10% 이내 정확도 ≥ 70%

---

## 🛠️ 다음 단계

1. **immediate_improvements.py 실행** - Phase 1 & 2 적용
2. **성능 재평가** - 개선 효과 측정
3. **반복 개선** - A/B 테스트로 최적 조합 찾기
