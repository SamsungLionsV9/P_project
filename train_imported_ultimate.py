"""
수입차 가격 예측 모델 - 최종 솔루션
수입차 특성에 최적화:
- 브랜드 계층 세분화 (럭셔리/프리미엄/일반)
- 브랜드 국적 구분 (독일/일본/미국)
- 강화된 Target Encoding
- 옵션 중요도 극대화
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
print("🌍 수입차 가격 예측 모델 - 최종 솔루션")
print("="*80)
print()

# ========== 1. 데이터 로드 ==========
print("📂 Step 1: 데이터 로드...")

df_raw = pd.read_csv('encar_imported_data.csv')
df_detail = pd.read_csv('data/complete_imported_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

print(f"✓ 수입차 데이터: {len(df):,}행")

# ========== 2. 전처리 ==========
print("\n🔧 Step 2: 전처리...")

df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])

# 수입차 가격 범위 (더 넓음)
df = df[df['Price'] > 300]
df = df[df['Price'] < 30000]  # 3억 이하
df = df[df['Mileage'] < 500000]
df = df[df['Year'] >= 2005]

# 로그 변환
df['Price_log'] = np.log1p(df['Price'])
print(f"✓ 전처리 후: {len(df):,}행")

# ========== 3. 수입차 특화 Feature Engineering (Part 1) ==========
print("\n⭐ Step 3: 수입차 특화 Feature Engineering...")

# 브랜드 계층 (수입차는 더 세분화)
luxury_brands = ['벤츠', 'Mercedes', 'BMW', '아우디', 'Audi', '렉서스', 'Lexus', 
                 '포르쉐', 'Porsche', '제네시스', 'Genesis', '테슬라', 'Tesla']
premium_brands = ['볼보', 'Volvo', '재규어', 'Jaguar', '랜드로버', 'Land Rover', 
                  '캐딜락', 'Cadillac', 'Infiniti', '인피니티']
standard_brands = ['폭스바겐', 'Volkswagen', '푸조', 'Peugeot', '시트로엥', 'Citroen',
                   'Mini', '미니', 'Jeep', '지프']

def classify_brand_tier(brand):
    brand = str(brand).lower()
    if any(b.lower() in brand for b in luxury_brands):
        return 'luxury'
    elif any(b.lower() in brand for b in premium_brands):
        return 'premium'
    elif any(b.lower() in brand for b in standard_brands):
        return 'standard'
    return 'budget'

df['brand_tier'] = df['Manufacturer'].apply(classify_brand_tier)

# 브랜드 국적 (감가율/신뢰도 다름)
german_brands = ['벤츠', 'Mercedes', 'BMW', '아우디', 'Audi', '폭스바겐', 'Volkswagen', '포르쉐']
japanese_brands = ['렉서스', 'Lexus', '토요타', 'Toyota', '혼다', 'Honda', '닛산', 'Nissan', 
                   '인피니티', 'Infiniti', '마쯔다', 'Mazda', '스바루']
american_brands = ['테슬라', 'Tesla', '캐딜락', 'Cadillac', 'Jeep', '지프', '쉐보레', 'Chevrolet']
european_brands = ['볼보', 'Volvo', '푸조', 'Peugeot', '시트로엥', '재규어', '랜드로버', 'Mini']

def classify_origin(brand):
    brand = str(brand).lower()
    if any(b.lower() in brand for b in german_brands):
        return 'german'
    elif any(b.lower() in brand for b in japanese_brands):
        return 'japanese'
    elif any(b.lower() in brand for b in american_brands):
        return 'american'
    elif any(b.lower() in brand for b in european_brands):
        return 'european'
    return 'other'

df['brand_origin'] = df['Manufacturer'].apply(classify_origin)

print(f"✓ 브랜드 계층 분류 완료")

# ========== 4. Target Encoding ==========
print("\n🎯 Step 4: Target Encoding...")

# Train/Test 분리
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# 분리 마커
train_df['is_train'] = 1
test_df['is_train'] = 0

# Target Encoding 함수
def create_target_encoding(train, test, col, target='Price_log', min_samples=10):
    global_mean = train[target].mean()
    agg = train.groupby(col)[target].agg(['mean', 'count'])
    counts = agg['count']
    means = agg['mean']
    
    # Smoothing
    smooth = 1 / (1 + np.exp(-(counts - min_samples) / 5))
    encoded = global_mean * (1 - smooth) + means * smooth
    
    train[f'{col}_target_enc'] = train[col].map(encoded).fillna(global_mean)
    test[f'{col}_target_enc'] = test[col].map(encoded).fillna(global_mean)
    
    return train, test, encoded

# Manufacturer Target Encoding (수입차는 브랜드가 매우 중요!)
train_df, test_df, brand_encoding = create_target_encoding(
    train_df, test_df, 'Manufacturer', 'Price_log', min_samples=50
)
print(f"✓ Manufacturer Target Encoding")

# Model Target Encoding
train_df, test_df, model_encoding = create_target_encoding(
    train_df, test_df, 'Model', 'Price_log', min_samples=20
)
print(f"✓ Model Target Encoding")

# 데이터 합치기
df = pd.concat([train_df, test_df], ignore_index=True)

# ========== 5. Feature Engineering (Part 2) ==========
print("\n⚙️ Step 5: Feature Engineering (Part 2)...")

current_year = 2025
df['age'] = current_year - df['Year']
df['age_squared'] = df['age'] ** 2
df['age_cubed'] = df['age'] ** 3

# Mileage
df['mileage_per_year'] = df['Mileage'] / (df['age'] + 1)
df['mileage_log'] = np.log1p(df['Mileage'])
df['mileage_squared'] = df['Mileage'] ** 2

# 옵션 (수입차는 옵션이 매우 중요!)
option_cols = [
    'has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key', 
    'has_rear_camera', 'has_led_lamp', 'has_parking_sensor', 'has_auto_ac',
    'has_heated_seat', 'has_ventilated_seat'
]

for col in option_cols:
    df[col] = df[col].fillna(0)

df['option_score'] = df[option_cols].sum(axis=1)
df['option_rate'] = df['option_score'] / 10

# 수입차 프리미엄 옵션 가중치 (더 높게)
premium_weights = {
    'has_sunroof': 2.5,
    'has_ventilated_seat': 2.5,
    'has_led_lamp': 2.0,
    'has_leather_seat': 2.0,
    'has_navigation': 1.5,
    'has_smart_key': 1.5,
    'has_rear_camera': 1.2,
    'has_parking_sensor': 1.2,
    'has_auto_ac': 1.0,
    'has_heated_seat': 1.0
}

df['option_weighted'] = sum(df[col] * weight for col, weight in premium_weights.items())

# 성능 등급
grade_map = {'excellent': 3, 'good': 2, 'normal': 1}
df['inspection_score'] = df['inspection_grade'].map(grade_map).fillna(1)

# 완벽한 조건
df['is_premium_condition'] = (
    (df['is_accident_free'] == 1) & 
    (df['inspection_score'] == 3) &
    (df['mileage_per_year'] < 12000)  # 수입차는 더 여유롭게
).astype(int)

df['is_full_option'] = (df['option_score'] >= 8).astype(int)

# 지역
df['region'] = df['region'].fillna('Unknown')
df['is_metro'] = (
    (df['region'].str.contains('서울')) | 
    (df['region'].str.contains('경기'))
).astype(int)

# 연료 (수입차는 디젤/하이브리드가 프리미엄)
df['is_diesel'] = (df['FuelType'].str.contains('디젤|경유', case=False, na=False)).astype(int)
df['is_hybrid'] = (df['FuelType'].str.contains('하이브리드|전기', case=False, na=False)).astype(int)
df['is_eco_fuel'] = (df['is_diesel'] | df['is_hybrid']).astype(int)

# 상호작용 (중요!)
df['brand_option_interaction'] = df['Manufacturer_target_enc'] * df['option_weighted']
df['model_option_interaction'] = df['Model_target_enc'] * df['option_weighted']
df['age_option_interaction'] = df['age'] * df['option_rate']
df['age_mileage_interaction'] = df['age'] * df['mileage_log']
df['tier_option_interaction'] = df['brand_tier'].map({
    'luxury': 4, 'premium': 3, 'standard': 2, 'budget': 1
}) * df['option_weighted']

# 가격 구간
price_bins = pd.qcut(df['Price'], q=10, labels=False, duplicates='drop')
df['price_segment'] = price_bins

print(f"✓ Feature Engineering 완료")

# ========== 6. Label Encoding ==========
print("\n🏷️ Step 6: 카테고리 인코딩...")

encoders = {}
for col in ['FuelType', 'brand_tier', 'brand_origin']:
    if col in df.columns:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

encoders['Manufacturer_target_enc'] = brand_encoding
encoders['Model_target_enc'] = model_encoding

# ========== 7. 학습 데이터 준비 ==========
print("\n📊 Step 7: 학습 데이터 준비...")

feature_cols = [
    # 기본
    'Year', 'age', 'age_squared', 'age_cubed',
    
    # 주행거리
    'Mileage', 'mileage_log', 'mileage_squared', 'mileage_per_year',
    
    # Target Encoding (핵심!)
    'Manufacturer_target_enc', 'Model_target_enc',
    
    # 브랜드 특성
    'brand_tier_encoded', 'brand_origin_encoded',
    
    # 카테고리
    'FuelType_encoded', 'price_segment', 
    'is_diesel', 'is_hybrid', 'is_eco_fuel',
    
    # 상태
    'is_accident_free', 'inspection_score', 'is_premium_condition',
    
    # 옵션 (수입차는 매우 중요!)
    *option_cols,
    'option_score', 'option_rate', 'option_weighted', 'is_full_option',
    
    # 지역
    'is_metro',
    
    # 상호작용
    'brand_option_interaction', 'model_option_interaction',
    'age_option_interaction', 'age_mileage_interaction',
    'tier_option_interaction'
]

# Train/Test 분리
train_df = df[df['is_train'] == 1].copy()
test_df = df[df['is_train'] == 0].copy()

X_train = train_df[feature_cols]
y_train = train_df['Price_log']
X_test = test_df[feature_cols]
y_test = test_df['Price_log']

print(f"✓ Feature: {len(feature_cols)}개")
print(f"✓ Train: {len(X_train):,}행")
print(f"✓ Test: {len(X_test):,}행")

# ========== 8. 모델 학습 ==========
print("\n🔥 Step 8: XGBoost 학습 (수입차 최적화)...")

model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.02,
    max_depth=7,              # 수입차는 복잡도 약간 높여도 OK
    min_child_weight=3,
    subsample=0.75,
    colsample_bytree=0.75,
    colsample_bylevel=0.75,
    gamma=0.5,
    reg_alpha=1.5,
    reg_lambda=4.0,
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

# ========== 9. 모델 평가 ==========
print("\n" + "="*80)
print("📈 Step 9: 모델 평가")
print("="*80)

# 로그 → 원래 가격
y_train_pred_log = model.predict(X_train)
y_test_pred_log = model.predict(X_test)

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
    print(f"   {row['feature']:40s}: {row['importance']:.4f}")

# ========== 10. 모델 저장 ==========
print("\n" + "="*80)
print("💾 Step 10: 모델 저장")
print("="*80)

os.makedirs('models', exist_ok=True)

joblib.dump(model, 'models/imported_ultimate.pkl')
joblib.dump(encoders, 'models/imported_ultimate_encoders.pkl')
joblib.dump(feature_cols, 'models/imported_ultimate_features.pkl')

metrics = {
    'train_mae': train_mae, 'train_r2': train_r2, 'train_rmse': train_rmse,
    'test_mae': test_mae, 'test_r2': test_r2, 'test_rmse': test_rmse,
    'n_samples': len(df), 'n_features': len(feature_cols),
    'overfitting_gap': train_r2 - test_r2,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
joblib.dump(metrics, 'models/imported_ultimate_metrics.pkl')

print(f"\n✅ 모델 저장 완료")

print("\n" + "="*80)
print("🎉 수입차 모델 학습 완료!")
print("="*80)
print(f"📊 최종 성능:")
print(f"   Test R²:  {test_r2:.4f}")
print(f"   Test MAE: {test_mae:.2f}만원")
print(f"   Overfit Gap: {train_r2 - test_r2:.4f}")
print(f"   데이터: {len(df):,}대")
print("="*80)
