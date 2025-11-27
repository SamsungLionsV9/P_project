"""
국산차 가격 예측 모델 V3 - 감가율(Depreciation) 기반
- 타겟: Price/MSRP (잔존가치율)
- 모델 서열이 MSRP로 자동 반영됨
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from msrp_data import DOMESTIC_MSRP, get_msrp

print("="*70)
print("🚗 국산차 가격 예측 모델 V3 - 감가율(Depreciation) 기반")
print("="*70)

# ========== 1. 데이터 로드 ==========
print("\n📂 Step 1: 데이터 로드...")
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
print(f"✓ 데이터: {len(df):,}행")

# ========== 2. 전처리 & 이상치 제거 ==========
print("\n🔧 Step 2: 전처리...")
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])
df = df[df['Price'] > 100]
df = df[df['Mileage'] < 350000]
df = df[df['Year'] >= 200800]

# 중복 제거
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')

# 패턴 이상치
pattern_prices = [111, 1111, 11111, 2222, 22222, 3333, 33333,
                  4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(pattern_prices)]

# 극단 가격
df = df[(df['Price'] >= 50) & (df['Price'] <= 50000)]

# 연식 추출
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['age'] = 2025 - df['YearOnly']

# 주행거리 이상치
df['km_per_year'] = df['Mileage'] / (df['age'] + 1)
df = df[(df['km_per_year'] <= 40000) & ((df['km_per_year'] >= 2000) | (df['age'] <= 1))]

# ========== 3. MSRP 추가 & 잔존가치율 계산 ==========
print("\n💰 Step 3: MSRP & 잔존가치율 계산...")

df['msrp'] = df['Model'].apply(lambda x: get_msrp(x, is_imported=False))
df['retention_rate'] = df['Price'] / df['msrp']  # 잔존가치율 (0~1)

# 이상치 제거: 잔존가치율 0.1~1.2 범위만 유지
# (10% 미만이거나 신차가보다 비싼 건 이상치)
before = len(df)
df = df[(df['retention_rate'] >= 0.1) & (df['retention_rate'] <= 1.2)]
print(f"✓ 잔존가치율 이상치 제거: {before:,} → {len(df):,}행")

# IQR 이상치 제거 (Model+Year별)
def remove_iqr_outliers(group):
    q1 = group['retention_rate'].quantile(0.25)
    q3 = group['retention_rate'].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return group[(group['retention_rate'] >= lower) & (group['retention_rate'] <= upper)]

df = df.groupby(['Model', 'YearOnly'], group_keys=False).apply(remove_iqr_outliers)
print(f"✓ 최종 데이터: {len(df):,}행")

# 잔존가치율 분포 확인
print(f"\n📊 잔존가치율 분포:")
print(f"   min: {df['retention_rate'].min():.2f}")
print(f"   mean: {df['retention_rate'].mean():.2f}")
print(f"   median: {df['retention_rate'].median():.2f}")
print(f"   max: {df['retention_rate'].max():.2f}")

# ========== 4. Feature Engineering ==========
print("\n⚙️ Step 4: Feature Engineering...")

# 기본 피처
df['age_squared'] = df['age'] ** 2
df['age_log'] = np.log1p(df['age'])
df['mileage_log'] = np.log1p(df['Mileage'])
df['mileage_squared'] = df['Mileage'] ** 2
df['mileage_per_year'] = df['Mileage'] / (df['age'] + 1)
df['msrp_log'] = np.log1p(df['msrp'])

# 주행거리 구간
def get_mileage_group(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    else: return 'E'

df['mileage_group'] = df['Mileage'].apply(get_mileage_group)

# 옵션 피처
option_cols = ['has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key',
               'has_rear_camera', 'has_led_lamp', 'has_heated_seat', 'has_ventilated_seat']
for col in option_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

df['option_count'] = sum(df[col] for col in option_cols if col in df.columns)
df['option_rate'] = df['option_count'] / 8

# 프리미엄 옵션 점수
df['option_premium'] = (
    df.get('has_sunroof', 0) * 2 + 
    df.get('has_leather_seat', 0) * 2 + 
    df.get('has_ventilated_seat', 0) * 2 +
    df.get('has_navigation', 0) + 
    df.get('has_smart_key', 0) + 
    df.get('has_led_lamp', 0)
)

# 연료
df['is_diesel'] = df['FuelType'].str.contains('디젤', na=False).astype(int)
df['is_hybrid'] = df['FuelType'].str.contains('하이브리드|전기', na=False).astype(int)

# 차급
def get_segment(model):
    m = str(model).lower()
    if 'g90' in m or 'gv90' in m: return 7
    elif 'g80' in m or 'gv80' in m: return 6
    elif 'g70' in m or 'gv70' in m: return 5
    elif any(x in m for x in ['팰리세이드', '모하비', '카니발', '스타리아']): return 5
    elif any(x in m for x in ['그랜저', 'k8', 'k9']): return 5
    elif any(x in m for x in ['싼타페', '쏘렌토']): return 4
    elif any(x in m for x in ['쏘나타', 'k5', 'k7']): return 3
    elif any(x in m for x in ['아반떼', 'k3', '투싼', '스포티지']): return 2
    elif any(x in m for x in ['모닝', '레이', '스파크']): return 1
    return 3

df['vehicle_class'] = df['Model'].apply(get_segment)

# ========== 5. Train/Test Split ==========
print("\n📊 Step 5: Train/Test 분리...")
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 6. 피처 선택 (타겟: retention_rate) ==========
feature_cols = [
    # MSRP (핵심!)
    'msrp', 'msrp_log',
    
    # 감가 요인
    'age', 'age_squared', 'age_log',
    'Mileage', 'mileage_log', 'mileage_squared', 'mileage_per_year',
    
    # 옵션 (잔존가치 영향)
    'option_count', 'option_rate', 'option_premium',
    'has_sunroof', 'has_leather_seat', 'has_smart_key', 'has_led_lamp',
    
    # 차급/연료
    'vehicle_class', 'is_diesel', 'is_hybrid',
]

# 피처 존재 확인
feature_cols = [c for c in feature_cols if c in train_df.columns]

X_train = train_df[feature_cols]
y_train = train_df['retention_rate']  # 잔존가치율!
X_test = test_df[feature_cols]
y_test = test_df['retention_rate']

print(f"✓ 피처: {len(feature_cols)}개")
print(f"✓ 타겟: retention_rate (잔존가치율)")

# ========== 7. 모델 학습 ==========
print("\n🔥 Step 6: 모델 학습...")

model = xgb.XGBRegressor(
    n_estimators=1000,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    early_stopping_rounds=50,
    random_state=42,
    verbosity=1
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=100
)

# ========== 8. 평가 ==========
print("\n" + "="*70)
print("📈 모델 평가 (잔존가치율 예측)")
print("="*70)

# 잔존가치율 예측
train_pred_rate = model.predict(X_train)
test_pred_rate = model.predict(X_test)

# 잔존가치율 기준 평가
train_r2 = r2_score(y_train, train_pred_rate)
test_r2 = r2_score(y_test, test_pred_rate)

print(f"\n잔존가치율 예측:")
print(f"🔵 Train R²: {train_r2:.4f}")
print(f"🟢 Test R²:  {test_r2:.4f}")

# 실제 가격으로 변환하여 평가
train_pred_price = train_pred_rate * train_df['msrp'].values
test_pred_price = test_pred_rate * test_df['msrp'].values

train_actual = train_df['Price'].values
test_actual = test_df['Price'].values

train_mae = mean_absolute_error(train_actual, train_pred_price)
test_mae = mean_absolute_error(test_actual, test_pred_price)

# MAPE (Mean Absolute Percentage Error)
train_mape = np.mean(np.abs(train_actual - train_pred_price) / train_actual) * 100
test_mape = np.mean(np.abs(test_actual - test_pred_price) / test_actual) * 100

print(f"\n가격 변환 후:")
print(f"🔵 Train MAE: {train_mae:.0f}만원, MAPE: {train_mape:.1f}%")
print(f"🟢 Test MAE:  {test_mae:.0f}만원, MAPE: {test_mape:.1f}%")

# Feature Importance
print(f"\n⭐ Feature Importance (상위 10개):")
importance = model.feature_importances_
feat_imp = sorted(zip(feature_cols, importance), key=lambda x: x[1], reverse=True)
for i, (feat, imp) in enumerate(feat_imp[:10], 1):
    print(f"   {i}. {feat}: {imp:.4f}")

# ========== 9. 저장 ==========
print("\n💾 Step 7: 모델 저장...")
joblib.dump(model, 'models/domestic_v3_depreciation.pkl')
joblib.dump(feature_cols, 'models/domestic_v3_features.pkl')
print("✅ 저장 완료!")

# ========== 10. 시뮬레이션 ==========
print("\n" + "="*70)
print("🧪 실제 예측 시뮬레이션 (V2 vs V3 비교)")
print("="*70)

def predict_v3(model_name, year, mileage, options=None):
    """V3 감가율 기반 예측"""
    age = 2025 - year
    msrp = get_msrp(model_name, is_imported=False)
    
    # 옵션 기본값
    if options is None:
        options = {'has_sunroof': 0.5, 'has_leather_seat': 0.5, 
                   'has_smart_key': 1, 'has_led_lamp': 0.5}
    
    features = {
        'msrp': msrp, 'msrp_log': np.log1p(msrp),
        'age': age, 'age_squared': age**2, 'age_log': np.log1p(age),
        'Mileage': mileage, 'mileage_log': np.log1p(mileage),
        'mileage_squared': mileage**2, 'mileage_per_year': mileage/(age+1),
        'option_count': 5, 'option_rate': 0.6, 'option_premium': 5,
        'has_sunroof': options.get('has_sunroof', 0.5),
        'has_leather_seat': options.get('has_leather_seat', 0.5),
        'has_smart_key': options.get('has_smart_key', 1),
        'has_led_lamp': options.get('has_led_lamp', 0.5),
        'vehicle_class': get_segment(model_name),
        'is_diesel': 0, 'is_hybrid': 0,
    }
    
    X = pd.DataFrame([features])[feature_cols]
    pred_rate = model.predict(X)[0]
    pred_price = pred_rate * msrp
    
    return pred_price, pred_rate, msrp

print("\n📊 모델 서열 테스트 (2022년 3만km):")
print("-"*60)

test_models = [
    ('모닝', '경차'),
    ('아반떼 (CN7)', '준중형'),
    ('쏘나타 (DN8)', '중형'),
    ('더 뉴 그랜저 IG', '대형'),
    ('G70', '제네시스'),
    ('G80 (RG3)', '제네시스'),
    ('G90', '제네시스'),
]

results = []
for model_name, seg in test_models:
    pred_price, pred_rate, msrp = predict_v3(model_name, 2022, 30000)
    results.append((model_name, seg, msrp, pred_rate, pred_price))
    print(f"  {seg:8} {model_name:20}: MSRP {msrp:,}만 × {pred_rate:.1%} = {pred_price:,.0f}만원")

# 서열 확인
print("\n✅ 서열 확인:")
prices = [r[4] for r in results]
correct_order = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
print(f"   모닝 < 아반떼 < 소나타 < 그랜저 < G70 < G80 < G90: {'✅ 정상!' if correct_order else '⚠️ 일부 역전'}")

# 연식 테스트
print("\n📊 연식별 감가율 테스트 (그랜저):")
print("-"*60)
for year in [2020, 2021, 2022, 2023, 2024]:
    pred_price, pred_rate, msrp = predict_v3('더 뉴 그랜저 IG', year, 30000)
    print(f"  {year}년: MSRP {msrp:,}만 × {pred_rate:.1%} = {pred_price:,.0f}만원")

print("\n" + "="*70)
print("✅ V3 감가율 모델 학습 완료!")
print("="*70)
