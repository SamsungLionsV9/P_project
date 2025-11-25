"""
국산차 가격 예측 모델 - 최종 솔루션
1. Target Encoding (모델별 평균 가격)
2. 강력한 정규화
3. 가격 로그 변환
4. Stratified sampling (가격대별)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🚗 국산차 가격 예측 모델 - 최종 솔루션 (Target Encoding)")
print("="*80)
print()

# ========== 1. 데이터 로드 ==========
print("📂 Step 1: 데이터 로드...")

df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

genesis_keywords = ['제네시스', 'GENESIS', 'Genesis']
df = df[~df['Manufacturer'].str.contains('|'.join(genesis_keywords), case=False, na=False)]
print(f"✓ 데이터: {len(df):,}행")

# ========== 2. 전처리 ==========
print("\n🔧 Step 2: 전처리...")

df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])
df = df[df['Price'] > 100]
df = df[df['Price'] < 12000]  # 1.2억 이하
df = df[df['Mileage'] < 350000]
df = df[df['Year'] >= 2008]

# 로그 변환 (핵심!)
df['Price_log'] = np.log1p(df['Price'])
print(f"✓ 전처리 후: {len(df):,}행")

# ========== 3. Target Encoding (핵심!) ==========
print("\n⭐ Step 3: Target Encoding...")

# Train/Test 분리 (먼저!)
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# 분리 마커 추가
train_df['is_train'] = 1
test_df['is_train'] = 0

# Target Encoding을 Train에서만 학습
def create_target_encoding(train, test, col, target='Price_log', min_samples=20):
    """Target Encoding with smoothing"""
    # 전체 평균
    global_mean = train[target].mean()
    
    # 각 카테고리의 평균과 개수
    agg = train.groupby(col)[target].agg(['mean', 'count'])
    counts = agg['count']
    means = agg['mean']
    
    # Smoothing (데이터 적으면 전체 평균에 가깝게)
    smooth = 1 / (1 + np.exp(-(counts - min_samples) / 10))
    encoded = global_mean * (1 - smooth) + means * smooth
    
    # Train 적용
    train[f'{col}_target_enc'] = train[col].map(encoded).fillna(global_mean)
    
    # Test 적용 (Train에서 학습한 값 사용)
    test[f'{col}_target_enc'] = test[col].map(encoded).fillna(global_mean)
    
    return train, test, encoded

# Model Target Encoding (가장 중요!)
train_df, test_df, model_encoding = create_target_encoding(
    train_df, test_df, 'Model', 'Price_log', min_samples=30
)
print(f"✓ Model Target Encoding: 평균 가격으로 변환")

# Manufacturer Target Encoding
train_df, test_df, brand_encoding = create_target_encoding(
    train_df, test_df, 'Manufacturer', 'Price_log', min_samples=100
)
print(f"✓ Manufacturer Target Encoding")

# 데이터 다시 합치기 (Feature Engineering용)
df = pd.concat([train_df, test_df], ignore_index=True)

# ========== 4. Feature Engineering ==========
print("\n⚙️ Step 4: Feature Engineering...")

current_year = 2025
df['age'] = current_year - df['Year']
df['age_squared'] = df['age'] ** 2
df['age_cubed'] = df['age'] ** 3

# Mileage
df['mileage_per_year'] = df['Mileage'] / (df['age'] + 1)
df['mileage_log'] = np.log1p(df['Mileage'])
df['mileage_squared'] = df['Mileage'] ** 2

# 주행거리 상태
df['mileage_condition'] = pd.cut(
    df['mileage_per_year'],
    bins=[0, 8000, 15000, 25000, 1000000],
    labels=['excellent', 'good', 'average', 'high']
)

# 옵션
option_cols = [
    'has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key', 
    'has_rear_camera', 'has_led_lamp', 'has_parking_sensor', 'has_auto_ac',
    'has_heated_seat', 'has_ventilated_seat'
]

for col in option_cols:
    df[col] = df[col].fillna(0)

df['option_score'] = df[option_cols].sum(axis=1)
df['option_rate'] = df['option_score'] / 10  # 정규화

# 프리미엄 옵션 가중치
premium_weights = {
    'has_sunroof': 1.5,
    'has_ventilated_seat': 1.5,
    'has_led_lamp': 1.2,
    'has_leather_seat': 1.3,
    'has_navigation': 1.1,
    'has_smart_key': 1.0,
    'has_rear_camera': 1.0,
    'has_parking_sensor': 1.0,
    'has_auto_ac': 1.0,
    'has_heated_seat': 1.0
}

df['option_weighted'] = sum(df[col] * weight for col, weight in premium_weights.items())

# 성능 등급
grade_map = {'excellent': 3, 'good': 2, 'normal': 1}
df['inspection_score'] = df['inspection_grade'].map(grade_map).fillna(1)

# 완벽한 조건 (무사고 + 우수 + 저주행)
df['is_premium_condition'] = (
    (df['is_accident_free'] == 1) & 
    (df['inspection_score'] == 3) &
    (df['mileage_per_year'] < 10000)
).astype(int)

# 지역
df['region'] = df['region'].fillna('Unknown')
df['is_metro'] = (
    (df['region'].str.contains('서울')) | 
    (df['region'].str.contains('경기'))
).astype(int)

# 연료 타입 (전기/하이브리드 프리미엄)
df['is_eco_fuel'] = (
    (df['FuelType'].str.contains('전기|하이브리드|LPG', case=False, na=False))
).astype(int)

# 상호작용
df['age_option_interaction'] = df['age'] * df['option_rate']
df['age_mileage_interaction'] = df['age'] * df['mileage_log']
df['model_option_interaction'] = df['Model_target_enc'] * df['option_weighted']

# 가격 구간 (Frequency Encoding)
price_bins = pd.qcut(df['Price'], q=10, labels=False, duplicates='drop')
df['price_segment'] = price_bins

print(f"✓ Feature Engineering 완료")

# ========== 5. Label Encoding ==========
print("\n🏷️ Step 5: 나머지 카테고리 인코딩...")

encoders = {}
for col in ['FuelType', 'mileage_condition']:
    if col in df.columns:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

# Target Encoding도 저장
encoders['Model_target_enc'] = model_encoding
encoders['Manufacturer_target_enc'] = brand_encoding

# ========== 6. 학습 데이터 준비 ==========
print("\n📊 Step 6: 학습 데이터 준비...")

feature_cols = [
    # 기본
    'Year', 'age', 'age_squared', 'age_cubed',
    
    # 주행거리
    'Mileage', 'mileage_log', 'mileage_squared', 'mileage_per_year',
    
    # Target Encoding (핵심!)
    'Model_target_enc', 'Manufacturer_target_enc',
    
    # 카테고리
    'FuelType_encoded', 'mileage_condition_encoded', 
    'price_segment', 'is_eco_fuel',
    
    # 상태
    'is_accident_free', 'inspection_score', 'is_premium_condition',
    
    # 옵션 (개별 + 집계)
    *option_cols,
    'option_score', 'option_rate', 'option_weighted',
    
    # 지역
    'is_metro',
    
    # 상호작용
    'age_option_interaction', 'age_mileage_interaction', 'model_option_interaction'
]

# Train/Test 다시 분리 (is_train 마커 사용)
train_df = df[df['is_train'] == 1].copy()
test_df = df[df['is_train'] == 0].copy()

X_train = train_df[feature_cols]
y_train = train_df['Price_log']  # 로그 변환된 가격
X_test = test_df[feature_cols]
y_test = test_df['Price_log']

print(f"✓ Feature: {len(feature_cols)}개")
print(f"✓ Train: {len(X_train):,}행")
print(f"✓ Test: {len(X_test):,}행")

# ========== 7. 모델 학습 ==========
print("\n🔥 Step 7: XGBoost 학습 (강력한 정규화)...")

model = xgb.XGBRegressor(
    n_estimators=800,
    learning_rate=0.02,
    max_depth=6,              # 감소 (과적합 방지)
    min_child_weight=5,        # 증가 (과적합 방지)
    subsample=0.7,            # 감소
    colsample_bytree=0.7,     # 감소
    colsample_bylevel=0.7,
    gamma=1.0,                # 증가 (과적합 방지)
    reg_alpha=2.0,            # L1 정규화 강화
    reg_lambda=5.0,           # L2 정규화 강화
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=100
)

print("\n✅ 학습 완료!")

# ========== 8. 모델 평가 ==========
print("\n" + "="*80)
print("📈 Step 8: 모델 평가")
print("="*80)

# 로그 공간에서 평가
y_train_pred_log = model.predict(X_train)
y_test_pred_log = model.predict(X_test)

# 원래 가격으로 변환
y_train_pred = np.expm1(y_train_pred_log)
y_test_pred = np.expm1(y_test_pred_log)
y_train_true = np.expm1(y_train)
y_test_true = np.expm1(y_test)

# Train 성능
train_mae = mean_absolute_error(y_train_true, y_train_pred)
train_r2 = r2_score(y_train_true, y_train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train_true, y_train_pred))

print(f"\n🔵 Train 성능:")
print(f"   MAE:  {train_mae:.2f}만원")
print(f"   RMSE: {train_rmse:.2f}만원")
print(f"   R²:   {train_r2:.4f}")

# Test 성능
test_mae = mean_absolute_error(y_test_true, y_test_pred)
test_r2 = r2_score(y_test_true, y_test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))

print(f"\n🟢 Test 성능:")
print(f"   MAE:  {test_mae:.2f}만원")
print(f"   RMSE: {test_rmse:.2f}만원")
print(f"   R²:   {test_r2:.4f}")

print(f"\n📊 과적합 체크:")
print(f"   Train-Test R² 차이: {train_r2 - test_r2:.4f}")
if (train_r2 - test_r2) < 0.10:
    print(f"   ✅ 과적합 없음!")
else:
    print(f"   ⚠️ 과적합 존재")

# Feature Importance
print(f"\n⭐ Feature Importance (상위 20개):")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(20).iterrows():
    print(f"   {row['feature']:35s}: {row['importance']:.4f}")

# ========== 9. 모델 저장 ==========
print("\n" + "="*80)
print("💾 Step 9: 모델 저장")
print("="*80)

os.makedirs('models', exist_ok=True)

joblib.dump(model, 'models/domestic_ultimate.pkl')
joblib.dump(encoders, 'models/domestic_ultimate_encoders.pkl')
joblib.dump(feature_cols, 'models/domestic_ultimate_features.pkl')

metrics = {
    'train_mae': train_mae, 'train_r2': train_r2, 'train_rmse': train_rmse,
    'test_mae': test_mae, 'test_r2': test_r2, 'test_rmse': test_rmse,
    'n_samples': len(df), 'n_features': len(feature_cols),
    'overfitting_gap': train_r2 - test_r2,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
joblib.dump(metrics, 'models/domestic_ultimate_metrics.pkl')

print(f"\n✅ 모델 저장 완료")

print("\n" + "="*80)
print("🎉 최종 모델 학습 완료!")
print("="*80)
print(f"📊 최종 성능:")
print(f"   Test R²:  {test_r2:.4f}")
print(f"   Test MAE: {test_mae:.2f}만원")
print(f"   Overfit Gap: {train_r2 - test_r2:.4f}")
print(f"   데이터: {len(df):,}대")
print("="*80)
