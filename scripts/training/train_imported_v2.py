"""
수입차 가격 예측 모델 V2
- 이상치(9999, 11111 등) 제거
- Model_Year_Mileage Target Encoding
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("🚗 수입차 가격 예측 모델 V2 - 이상치 제거")
print("="*70)

# ========== 1. 데이터 로드 ==========
print("\n📂 Step 1: 데이터 로드...")
df_raw = pd.read_csv('encar_imported_data.csv')
df_detail = pd.read_csv('data/complete_imported_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
print(f"✓ 원본 데이터: {len(df):,}행")

# ========== 2. 전처리 & 이상치 제거 (강화) ==========
print("\n🔧 Step 2: 전처리 & 이상치 제거 (강화)...")
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model', 'Manufacturer'])
df = df[df['Price'] > 300]
df = df[df['Mileage'] < 300000]
df = df[df['Year'] >= 201000]

before = len(df)

# 0단계: 중복 데이터 제거
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')
print(f"✓ 중복 제거: {before:,} → {len(df):,}행")

# 1단계: 패턴 가격 이상치 제거
pattern_prices = [111, 1111, 11111, 2222, 22222, 3333, 33333,
                  4444, 5555, 6666, 7777, 8888, 9999, 99999, 1234, 4321, 12345, 54321, 10000]
before2 = len(df)
df = df[~df['Price'].isin(pattern_prices)]
print(f"✓ 패턴 이상치 제거: {before2:,} → {len(df):,}행")

# 1.5단계: 극단 가격 제거 (NEW!)
before_extreme = len(df)
df = df[df['Price'] >= 100]  # 100만원 이상 (수입차)
df = df[df['Price'] <= 100000]  # 10억원 이하 (수입차)
print(f"✓ 극단 가격 제거 (<100만, >10억): {before_extreme:,} → {len(df):,}행")

# 2단계: 연간 주행거리 이상치 제거
df['YearOnly_temp'] = (df['Year'] // 100).astype(int)
df['age_temp'] = 2025 - df['YearOnly_temp']
df['km_per_year'] = df['Mileage'] / (df['age_temp'] + 1)
before3 = len(df)
df = df[df['km_per_year'] <= 40000]
df = df[(df['km_per_year'] >= 2000) | (df['age_temp'] <= 1)]
print(f"✓ 주행거리 이상치 제거: {before3:,} → {len(df):,}행")

# 2.5단계: 허위 매물 제거 - 신차 대비 과도 감가 (NEW!)
before_fake = len(df)
recent_mask = df['age_temp'] <= 2  # 1~2년차
model_mean = df.groupby('Model')['Price'].transform('mean')
fake_mask = (df['Price'] < model_mean * 0.4) & recent_mask  # 평균의 40% 미만
df = df[~fake_mask]
df = df.drop(columns=['age_temp', 'km_per_year'])
print(f"✓ 허위매물 제거: {before_fake:,} → {len(df):,}행")

# 3단계: IQR 1.5배 이상치 제거 (3σ → IQR로 변경)
def remove_iqr_outliers(group):
    q1 = group['Price'].quantile(0.25)
    q3 = group['Price'].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return group[(group['Price'] >= lower) & (group['Price'] <= upper)]

before4 = len(df)
df = df.groupby(['Model', 'YearOnly_temp'], group_keys=False).apply(remove_iqr_outliers)
df = df.drop(columns=['YearOnly_temp'])
print(f"✓ IQR 1.5배 이상치 제거: {before4:,} → {len(df):,}행")

# 4단계: Log 변환 후 Z-score > 3 제거 (NEW!)
df['Price_log_temp'] = np.log1p(df['Price'])
z_mean = df['Price_log_temp'].mean()
z_std = df['Price_log_temp'].std()
df['log_z_score'] = (df['Price_log_temp'] - z_mean) / z_std
before5 = len(df)
df = df[abs(df['log_z_score']) <= 3]
df = df.drop(columns=['Price_log_temp', 'log_z_score'])
print(f"✓ Log Z-score>3 제거: {before5:,} → {len(df):,}행")
print(f"✓ 최종: {len(df):,}행")

# 연식 추출
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['age'] = 2025 - df['YearOnly']
df['Price_log'] = np.log1p(df['Price'])
df['mileage_log'] = np.log1p(df['Mileage'])

# 주행거리 구간
def get_mileage_group(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    else: return 'E'

df['mileage_group'] = df['Mileage'].apply(get_mileage_group)

# 브랜드 정리
df['Brand'] = df['Manufacturer'].str.strip()
print(f"✓ 최종 데이터: {len(df):,}행")
print(f"✓ 브랜드: {df['Brand'].nunique()}개")

# ========== 3. Train/Test Split ==========
print("\n📊 Step 3: Train/Test 분리...")
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_df = train_df.copy()
test_df = test_df.copy()
print(f"✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 4. Target Encoding ==========
print("\n⭐ Step 4: Target Encoding...")

def create_target_encoding(train, test, col, target='Price_log', min_samples=5):
    global_mean = train[target].mean()
    stats = train.groupby(col)[target].agg(['mean', 'count'])
    smoothing = 1 / (1 + np.exp(-(stats['count'] - min_samples) / 3))
    stats['smoothed'] = global_mean * (1 - smoothing) + stats['mean'] * smoothing
    encoding = stats['smoothed'].to_dict()
    encoding['__default__'] = global_mean
    train[f'{col}_enc'] = train[col].map(encoding).fillna(global_mean)
    test[f'{col}_enc'] = test[col].map(encoding).fillna(global_mean)
    return train, test, encoding

# Brand Encoding
train_df, test_df, brand_enc = create_target_encoding(train_df, test_df, 'Brand', min_samples=50)
print(f"✓ Brand Encoding: {len(brand_enc)}개")

# Model Encoding
train_df, test_df, model_enc = create_target_encoding(train_df, test_df, 'Model', min_samples=10)
print(f"✓ Model Encoding: {len(model_enc)}개")

# Model + Year Encoding
train_df['Model_Year'] = train_df['Model'] + '_' + train_df['YearOnly'].astype(str)
test_df['Model_Year'] = test_df['Model'] + '_' + test_df['YearOnly'].astype(str)
train_df, test_df, model_year_enc = create_target_encoding(train_df, test_df, 'Model_Year', min_samples=5)
print(f"✓ Model+Year Encoding: {len(model_year_enc)}개")

# Model + Year + Mileage Encoding (핵심!)
train_df['Model_Year_Mileage'] = train_df['Model'] + '_' + train_df['YearOnly'].astype(str) + '_' + train_df['mileage_group']
test_df['Model_Year_Mileage'] = test_df['Model'] + '_' + test_df['YearOnly'].astype(str) + '_' + test_df['mileage_group']
train_df, test_df, mym_enc = create_target_encoding(train_df, test_df, 'Model_Year_Mileage', min_samples=3)
print(f"✓ Model+Year+Mileage Encoding: {len(mym_enc)}개")

# ========== 5. Feature Engineering ==========
print("\n⚙️ Step 5: Feature Engineering...")

def engineer_features(df):
    df = df.copy()
    df['age_squared'] = df['age'] ** 2
    df['age_log'] = np.log1p(df['age'])
    df['mileage_per_year'] = df['Mileage'] / (df['age'] + 1)
    df['mileage_squared'] = df['Mileage'] ** 2
    
    option_cols = ['has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key',
                   'has_rear_camera', 'has_led_lamp', 'has_parking_sensor', 'has_auto_ac']
    for col in option_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
        else:
            df[col] = 0
    df['option_count'] = df[option_cols].sum(axis=1)
    df['option_rate'] = df['option_count'] / 8
    
    df['is_accident_free'] = df['is_accident_free'].fillna(1) if 'is_accident_free' in df.columns else 1
    
    # 브랜드 티어
    def get_brand_tier(brand):
        luxury = ['벤츠', 'Mercedes-Benz', 'BMW', '아우디', 'Audi', '포르쉐', 'Porsche', '렉서스', 'Lexus']
        premium = ['볼보', 'Volvo', '재규어', 'Jaguar', '랜드로버', 'Land Rover', '인피니티']
        for b in luxury:
            if b in str(brand): return 3
        for b in premium:
            if b in str(brand): return 2
        return 1
    df['brand_tier'] = df['Brand'].apply(get_brand_tier)
    
    # 상호작용
    df['enc_x_age'] = df['Model_Year_Mileage_enc'] * df['age']
    df['enc_x_mileage'] = df['Model_Year_Mileage_enc'] * df['mileage_log']
    df['enc_x_option'] = df['Model_Year_Mileage_enc'] * df['option_rate']
    
    return df

train_df = engineer_features(train_df)
test_df = engineer_features(test_df)

# ========== 6. 학습 ==========
print("\n🔥 Step 6: 모델 학습...")

feature_cols = [
    'Brand_enc', 'Model_enc', 'Model_Year_enc', 'Model_Year_Mileage_enc',
    'age', 'age_squared', 'age_log',
    'Mileage', 'mileage_log', 'mileage_squared', 'mileage_per_year',
    'option_count', 'option_rate',
    'is_accident_free', 'brand_tier',
    'enc_x_age', 'enc_x_mileage', 'enc_x_option'
]

X_train = train_df[feature_cols]
y_train = train_df['Price_log']
X_test = test_df[feature_cols]
y_test = test_df['Price_log']

model = xgb.XGBRegressor(
    n_estimators=800,
    learning_rate=0.02,
    max_depth=7,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=100)

# ========== 7. 평가 ==========
print("\n" + "="*70)
print("📈 모델 평가")
print("="*70)

train_pred = model.predict(X_train)
test_pred = model.predict(X_test)
train_price = np.expm1(train_pred)
test_price = np.expm1(test_pred)
train_actual = np.expm1(y_train)
test_actual = np.expm1(y_test)

print(f"🔵 Train: R²={r2_score(y_train, train_pred):.4f}, MAE={mean_absolute_error(train_actual, train_price):.0f}만원")
print(f"🟢 Test:  R²={r2_score(y_test, test_pred):.4f}, MAE={mean_absolute_error(test_actual, test_price):.0f}만원")

# ========== 8. 저장 ==========
print("\n💾 Step 8: 저장...")
encoders = {
    'Brand_enc': brand_enc,
    'Model_enc': model_enc,
    'Model_Year_enc': model_year_enc,
    'Model_Year_Mileage_enc': mym_enc
}

joblib.dump(model, 'models/imported_v2.pkl')
joblib.dump(encoders, 'models/imported_v2_encoders.pkl')
joblib.dump(feature_cols, 'models/imported_v2_features.pkl')
joblib.dump({
    'train_r2': r2_score(y_train, train_pred),
    'test_r2': r2_score(y_test, test_pred),
    'test_mae': mean_absolute_error(test_actual, test_price)
}, 'models/imported_v2_metrics.pkl')

print("✅ 수입차 V2 모델 저장 완료!")

# ========== 9. 예측 테스트 ==========
print("\n🧪 예측 테스트")
print("-"*50)

def predict_price(brand, model_name, year, mileage):
    mg = 'A' if mileage < 30000 else ('B' if mileage < 60000 else ('C' if mileage < 100000 else 'D'))
    
    brand_enc_val = brand_enc.get(brand, brand_enc.get('__default__', 8.0))
    model_enc_val = model_enc.get(model_name, model_enc.get('__default__', 8.0))
    my_key = f"{model_name}_{year}"
    my_enc_val = model_year_enc.get(my_key, model_enc_val)
    mym_key = f"{model_name}_{year}_{mg}"
    mym_enc_val = mym_enc.get(mym_key, my_enc_val)
    
    luxury = ['벤츠', 'Mercedes-Benz', 'BMW', '아우디', 'Audi', '포르쉐']
    brand_tier = 3 if any(b in brand for b in luxury) else 2
    
    age = 2025 - year
    features = {
        'Brand_enc': brand_enc_val, 'Model_enc': model_enc_val, 
        'Model_Year_enc': my_enc_val, 'Model_Year_Mileage_enc': mym_enc_val,
        'age': age, 'age_squared': age**2, 'age_log': np.log1p(age),
        'Mileage': mileage, 'mileage_log': np.log1p(mileage), 'mileage_squared': mileage**2,
        'mileage_per_year': mileage/(age+1),
        'option_count': 6, 'option_rate': 0.75,
        'is_accident_free': 1, 'brand_tier': brand_tier,
        'enc_x_age': mym_enc_val * age,
        'enc_x_mileage': mym_enc_val * np.log1p(mileage),
        'enc_x_option': mym_enc_val * 0.75
    }
    X = pd.DataFrame([features])[feature_cols]
    return np.expm1(model.predict(X)[0])

# 테스트
tests = [
    ('BMW', '5시리즈', 2021, 40000),
    ('벤츠', 'E-Class', 2020, 50000),
    ('아우디', 'A6', 2020, 50000),
    ('BMW', 'X5', 2021, 45000)
]

for brand, m, y, km in tests:
    subset = df[(df['Model'].str.contains(m.replace('-',''), na=False)) & (df['YearOnly']==y) & 
                (df['Mileage']>=km-20000) & (df['Mileage']<=km+20000)]
    actual = subset['Price'].mean() if len(subset) > 0 else 0
    pred = predict_price(brand, m, y, km)
    if actual > 0:
        error = abs(pred - actual) / actual * 100
        status = "✅" if error < 15 else ("⚠️" if error < 25 else "❌")
        print(f"{status} {brand} {m} {y}년: 예측 {pred:,.0f}만원 / 실제 {actual:,.0f}만원 (오차 {error:.1f}%)")
    else:
        print(f"   {brand} {m} {y}년: 예측 {pred:,.0f}만원 (비교 데이터 없음)")
