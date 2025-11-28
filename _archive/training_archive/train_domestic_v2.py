"""
국산차 가격 예측 모델 V2
- price_segment 제거 (Data Leakage 해결)
- Model + Year + Mileage 구간 Target Encoding (핵심)
- 신차가격(MSRP) 기반 감가율 피처 추가
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
print("🚗 국산차 가격 예측 모델 V2 - Data Leakage 해결")
print("="*70)

# ========== 1. 데이터 로드 ==========
print("\n📂 Step 1: 데이터 로드...")
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

# 제네시스 포함! (국산 고급 브랜드)
print(f"✓ 데이터 (제네시스 포함): {len(df):,}행")

# ========== 2. 전처리 & 이상치 제거 (강화) ==========
print("\n🔧 Step 2: 전처리 & 이상치 제거 (강화)...")
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])
df = df[df['Price'] > 100]
df = df[df['Mileage'] < 350000]
df = df[df['Year'] >= 200800]  # 2008년 이후

before = len(df)

# 0단계: 중복 데이터 제거 (핵심!)
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')
print(f"✓ 중복 제거: {before:,} → {len(df):,}행")

# 1단계: 패턴 가격 이상치 제거
pattern_prices = [
    111, 1111, 11111, 2222, 22222, 3333, 33333,
    4444, 5555, 6666, 7777, 8888, 9999, 99999,
    1234, 4321, 12345, 54321
]
before2 = len(df)
df = df[~df['Price'].isin(pattern_prices)]
print(f"✓ 패턴 이상치 제거: {before2:,} → {len(df):,}행")

# 1.5단계: 극단 가격 제거 (NEW!)
before_extreme = len(df)
df = df[df['Price'] >= 50]  # 50만원 이상
df = df[df['Price'] <= 50000]  # 5억원 이하
print(f"✓ 극단 가격 제거 (<50만, >5억): {before_extreme:,} → {len(df):,}행")

# 2단계: 연간 주행거리 이상치 제거
df['YearOnly_temp'] = (df['Year'] // 100).astype(int)
df['age_temp'] = 2025 - df['YearOnly_temp']
df['km_per_year'] = df['Mileage'] / (df['age_temp'] + 1)
before3 = len(df)
df = df[df['km_per_year'] <= 40000]  # 연 4만km 이하
df = df[(df['km_per_year'] >= 2000) | (df['age_temp'] <= 1)]  # 연 2000km 이상 또는 1년 이하
print(f"✓ 주행거리 이상치 제거: {before3:,} → {len(df):,}행")

# 2.5단계: 허위 매물 제거 - 신차 대비 과도 감가 (NEW!)
before_fake = len(df)
recent_mask = df['age_temp'] <= 2  # 1~2년차
model_mean = df.groupby('Model')['Price'].transform('mean')
fake_mask = (df['Price'] < model_mean * 0.4) & recent_mask  # 평균의 40% 미만
df = df[~fake_mask]
df = df.drop(columns=['age_temp', 'km_per_year'])
print(f"✓ 허위매물 제거 (최신연식+과도감가): {before_fake:,} → {len(df):,}행")

# 3단계: 모델+연식별 IQR 1.5배 이상치 제거 (3σ → IQR로 변경)
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

# 4단계: Log 변환 후 Z-score > 3 제거 (전체 분포 기준, NEW!)
df['Price_log_temp'] = np.log1p(df['Price'])
z_mean = df['Price_log_temp'].mean()
z_std = df['Price_log_temp'].std()
df['log_z_score'] = (df['Price_log_temp'] - z_mean) / z_std
before5 = len(df)
df = df[abs(df['log_z_score']) <= 3]
df = df.drop(columns=['Price_log_temp', 'log_z_score'])
print(f"✓ Log Z-score>3 제거: {before5:,} → {len(df):,}행")

# 연식 추출
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['age'] = 2025 - df['YearOnly']

# 로그 변환
df['Price_log'] = np.log1p(df['Price'])
df['mileage_log'] = np.log1p(df['Mileage'])

# 주행거리 구간 (5단계로 세분화!)
def get_mileage_group(m):
    if m < 30000:
        return 'A'        # 0-3만km (신차급)
    elif m < 60000:
        return 'B'        # 3-6만km (저주행)
    elif m < 100000:
        return 'C'        # 6-10만km (보통)
    elif m < 150000:
        return 'D'        # 10-15만km (고주행)
    else:
        return 'E'        # 15만km+ (매우 고주행)

df['mileage_group'] = df['Mileage'].apply(get_mileage_group)
print(f"✓ 전처리 후: {len(df):,}행")

# ========== 3. Train/Test Split (먼저!) ==========
print("\n📊 Step 3: Train/Test 분리...")
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_df = train_df.copy()
test_df = test_df.copy()
print(f"✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 4. Target Encoding (Train에서만 학습!) ==========
print("\n⭐ Step 4: Target Encoding...")

def create_target_encoding(train, test, col, target='Price_log', min_samples=10):
    """Smoothed Target Encoding - Train에서만 학습"""
    global_mean = train[target].mean()
    
    # Train에서 통계 계산
    stats = train.groupby(col)[target].agg(['mean', 'count'])
    smoothing = 1 / (1 + np.exp(-(stats['count'] - min_samples) / 5))
    stats['smoothed'] = global_mean * (1 - smoothing) + stats['mean'] * smoothing
    
    encoding = stats['smoothed'].to_dict()
    encoding['__default__'] = global_mean
    
    # 적용
    train[f'{col}_enc'] = train[col].map(encoding).fillna(global_mean)
    test[f'{col}_enc'] = test[col].map(encoding).fillna(global_mean)
    
    return train, test, encoding

# (1) Model Target Encoding
train_df, test_df, model_enc = create_target_encoding(train_df, test_df, 'Model', min_samples=30)
print(f"✓ Model Encoding: {len(model_enc)}개 모델")

# (2) Manufacturer Target Encoding  
train_df, test_df, mfr_enc = create_target_encoding(train_df, test_df, 'Manufacturer', min_samples=100)
print(f"✓ Manufacturer Encoding: {len(mfr_enc)}개 브랜드")

# (3) Model + Year Target Encoding
train_df['Model_Year'] = train_df['Model'] + '_' + train_df['YearOnly'].astype(str)
test_df['Model_Year'] = test_df['Model'] + '_' + test_df['YearOnly'].astype(str)
train_df, test_df, model_year_enc = create_target_encoding(train_df, test_df, 'Model_Year', min_samples=10)
print(f"✓ Model+Year Encoding: {len(model_year_enc)}개 조합")

# (4) ⭐ Model + Year + Mileage 구간 Target Encoding (핵심!)
train_df['Model_Year_Mileage'] = train_df['Model'] + '_' + train_df['YearOnly'].astype(str) + '_' + train_df['mileage_group']
test_df['Model_Year_Mileage'] = test_df['Model'] + '_' + test_df['YearOnly'].astype(str) + '_' + test_df['mileage_group']
train_df, test_df, model_year_mileage_enc = create_target_encoding(train_df, test_df, 'Model_Year_Mileage', min_samples=5)
print(f"✓ Model+Year+Mileage Encoding: {len(model_year_mileage_enc)}개 조합 (핵심!)")

# ========== 5. Feature Engineering ==========
print("\n⚙️ Step 5: Feature Engineering...")

def engineer_features(df):
    """피처 엔지니어링"""
    df = df.copy()
    
    # 연식 관련
    df['age_squared'] = df['age'] ** 2
    df['age_log'] = np.log1p(df['age'])
    
    # 주행거리 관련
    df['mileage_per_year'] = df['Mileage'] / (df['age'] + 1)
    df['mileage_squared'] = df['Mileage'] ** 2
    
    # 옵션
    option_cols = ['has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key',
                   'has_rear_camera', 'has_led_lamp', 'has_parking_sensor', 'has_auto_ac',
                   'has_heated_seat', 'has_ventilated_seat']
    
    for col in option_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
        else:
            df[col] = 0
    
    df['option_count'] = df[option_cols].sum(axis=1)
    df['option_rate'] = df['option_count'] / 10
    
    # 프리미엄 옵션 가중치
    df['option_premium'] = (
        df['has_sunroof'] * 1.5 + 
        df['has_ventilated_seat'] * 1.5 + 
        df['has_led_lamp'] * 1.2 +
        df['has_leather_seat'] * 1.3 +
        df['option_count'] * 0.5
    )
    
    # 상태
    df['is_accident_free'] = df['is_accident_free'].fillna(1)
    
    # 연료
    df['is_diesel'] = df['FuelType'].str.contains('디젤', na=False).astype(int)
    df['is_lpg'] = df['FuelType'].str.contains('LPG', na=False).astype(int)
    df['is_hybrid'] = df['FuelType'].str.contains('하이브리드|전기', na=False).astype(int)
    
    # 차급 추정 (세분화!)
    def get_segment(model):
        m = str(model).lower()
        # 제네시스 (프리미엄)
        if 'g90' in m or 'gv90' in m:
            return 7  # 최고급
        elif 'g80' in m or 'gv80' in m:
            return 6  # 고급
        elif 'g70' in m or 'gv70' in m:
            return 5  # 준고급
        # SUV
        elif any(x in m for x in ['팰리세이드', '모하비']):
            return 5  # 대형 SUV
        elif any(x in m for x in ['싼타페', '쏘렌토']):
            return 4  # 중형 SUV
        elif any(x in m for x in ['투싼', '스포티지', '셀토스', '니로']):
            return 3  # 준중형 SUV
        elif any(x in m for x in ['코나', '베뉴', '티볼리']):
            return 2  # 소형 SUV
        # MPV
        elif any(x in m for x in ['카니발', '스타리아']):
            return 5  # 대형 MPV
        elif '스타렉스' in m:
            return 4  # 중형 MPV
        # 세단
        elif any(x in m for x in ['k9', '에쿠스']):
            return 6  # 최고급 세단
        elif any(x in m for x in ['그랜저', 'k8']):
            return 5  # 고급 세단
        elif any(x in m for x in ['k7', '제네시스 세단']):
            return 4  # 준고급 세단
        elif any(x in m for x in ['쏘나타', 'k5']):
            return 3  # 중형 세단
        elif any(x in m for x in ['아반떼', 'k3']):
            return 2  # 준중형 세단
        elif any(x in m for x in ['모닝', '레이', '캐스퍼', '스파크']):
            return 1  # 소형/경차
        return 3  # 기본값
    
    df['vehicle_class'] = df['Model'].apply(get_segment)
    
    # 신차가격(MSRP) 추가 - 모델 서열 반영!
    df['msrp'] = df['Model'].apply(lambda x: get_msrp(x, is_imported=False))
    df['msrp_log'] = np.log1p(df['msrp'])
    
    # 감가율 = 현재가격 / 신차가격 (Data Leakage 주의: 비율만 학습에 사용)
    # → 학습에는 msrp만 사용하고, 예측 시 msrp 기반으로 가격 범위 추정 가능
    df['depreciation_ratio'] = df['Price'] / df['msrp']  # 0~1 사이 값
    
    # 연간 감가율 = (1 - 감가율) / 연식
    df['annual_depreciation'] = (1 - df['depreciation_ratio']) / (df['age'] + 1)
    
    # 상호작용 피처
    df['enc_x_age'] = df['Model_Year_Mileage_enc'] * df['age']
    df['enc_x_mileage'] = df['Model_Year_Mileage_enc'] * df['mileage_log']
    df['enc_x_option'] = df['Model_Year_Mileage_enc'] * df['option_rate']
    df['msrp_x_age'] = df['msrp_log'] * df['age']  # 신차가격 × 연식
    df['msrp_x_mileage'] = df['msrp_log'] * df['mileage_log']  # 신차가격 × 주행거리
    
    return df

train_df = engineer_features(train_df)
test_df = engineer_features(test_df)
print("✓ Feature Engineering 완료")

# ========== 6. 학습 ==========
print("\n🔥 Step 6: 모델 학습...")

# 피처 선택 (price_segment 없음!)
feature_cols = [
    # Target Encoding (핵심)
    'Model_enc', 'Manufacturer_enc', 'Model_Year_enc', 'Model_Year_Mileage_enc',
    
    # 신차가격(MSRP) - 모델 서열 반영!
    'msrp', 'msrp_log',
    
    # 기본
    'age', 'age_squared', 'age_log',
    'Mileage', 'mileage_log', 'mileage_squared', 'mileage_per_year',
    
    # 옵션
    'option_count', 'option_rate', 'option_premium',
    'has_sunroof', 'has_led_lamp', 'has_leather_seat', 'has_smart_key',
    
    # 상태/연료
    'is_accident_free', 'is_diesel', 'is_lpg', 'is_hybrid',
    
    # 차급
    'vehicle_class',
    
    # 상호작용
    'enc_x_age', 'enc_x_mileage', 'enc_x_option',
    'msrp_x_age', 'msrp_x_mileage'  # 신차가격 상호작용
]

X_train = train_df[feature_cols]
y_train = train_df['Price_log']
X_test = test_df[feature_cols]
y_test = test_df['Price_log']

print(f"✓ 피처: {len(feature_cols)}개")

# XGBoost 학습
model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.02,
    max_depth=7,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0.3,
    reg_alpha=0.5,
    reg_lambda=2.0,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=100
)

# ========== 7. 평가 ==========
print("\n" + "="*70)
print("📈 모델 평가")
print("="*70)

# Train 성능
train_pred = model.predict(X_train)
train_price = np.expm1(train_pred)
train_actual = np.expm1(y_train)

# Test 성능
test_pred = model.predict(X_test)
test_price = np.expm1(test_pred)
test_actual = np.expm1(y_test)

print(f"\n🔵 Train: R²={r2_score(y_train, train_pred):.4f}, MAE={mean_absolute_error(train_actual, train_price):.0f}만원")
print(f"🟢 Test:  R²={r2_score(y_test, test_pred):.4f}, MAE={mean_absolute_error(test_actual, test_price):.0f}만원")

gap = r2_score(y_train, train_pred) - r2_score(y_test, test_pred)
print(f"\n📊 과적합 체크: {gap:.4f} {'✅ OK' if gap < 0.05 else '⚠️ 주의'}")

# Feature Importance
print("\n⭐ Feature Importance (상위 10개):")
importance = dict(zip(feature_cols, model.feature_importances_))
for i, (k, v) in enumerate(sorted(importance.items(), key=lambda x: -x[1])[:10]):
    print(f"   {i+1}. {k}: {v:.4f}")

# ========== 8. 저장 ==========
print("\n💾 Step 8: 모델 저장...")

# 인코더 저장
encoders = {
    'Model_enc': model_enc,
    'Manufacturer_enc': mfr_enc,
    'Model_Year_enc': model_year_enc,
    'Model_Year_Mileage_enc': model_year_mileage_enc
}

joblib.dump(model, 'models/domestic_v2.pkl')
joblib.dump(encoders, 'models/domestic_v2_encoders.pkl')
joblib.dump(feature_cols, 'models/domestic_v2_features.pkl')
joblib.dump({
    'train_r2': r2_score(y_train, train_pred),
    'test_r2': r2_score(y_test, test_pred),
    'test_mae': mean_absolute_error(test_actual, test_price)
}, 'models/domestic_v2_metrics.pkl')

print("✅ 저장 완료!")

# ========== 9. 실제 예측 시뮬레이션 ==========
print("\n" + "="*70)
print("🧪 실제 예측 시뮬레이션")
print("="*70)

def predict_price(model_name, year, mileage, brand='현대'):
    """실제 API와 동일한 예측 로직"""
    # 주행거리 구간 (5단계)
    if mileage < 30000:
        mg = 'A'
    elif mileage < 60000:
        mg = 'B'
    elif mileage < 100000:
        mg = 'C'
    elif mileage < 150000:
        mg = 'D'
    else:
        mg = 'E'
    
    # Target Encoding 조회
    model_enc_val = model_enc.get(model_name, model_enc.get('__default__', 7.5))
    mfr_enc_val = mfr_enc.get(brand, mfr_enc.get('__default__', 7.5))
    my_key = f"{model_name}_{year}"
    my_enc_val = model_year_enc.get(my_key, model_enc_val)
    mym_key = f"{model_name}_{year}_{mg}"
    mym_enc_val = model_year_mileage_enc.get(mym_key, my_enc_val)
    
    # 피처 생성
    age = 2025 - year
    msrp = get_msrp(model_name, is_imported=False)
    msrp_log = np.log1p(msrp)
    
    features = {
        'Model_enc': model_enc_val,
        'Manufacturer_enc': mfr_enc_val,
        'Model_Year_enc': my_enc_val,
        'Model_Year_Mileage_enc': mym_enc_val,
        'msrp': msrp, 'msrp_log': msrp_log,
        'age': age, 'age_squared': age**2, 'age_log': np.log1p(age),
        'Mileage': mileage, 'mileage_log': np.log1p(mileage),
        'mileage_squared': mileage**2, 'mileage_per_year': mileage/(age+1),
        'option_count': 6, 'option_rate': 0.6, 'option_premium': 5.0,
        'has_sunroof': 0.5, 'has_led_lamp': 0.5, 'has_leather_seat': 0.5, 'has_smart_key': 1,
        'is_accident_free': 1, 'is_diesel': 0, 'is_lpg': 0, 'is_hybrid': 0,
        'vehicle_class': 3,
        'enc_x_age': mym_enc_val * age,
        'enc_x_mileage': mym_enc_val * np.log1p(mileage),
        'enc_x_option': mym_enc_val * 0.6,
        'msrp_x_age': msrp_log * age,
        'msrp_x_mileage': msrp_log * np.log1p(mileage)
    }
    
    X = pd.DataFrame([features])[feature_cols]
    pred_log = model.predict(X)[0]
    return np.expm1(pred_log)

# 테스트 케이스
test_cases = [
    ('더 뉴 그랜저 IG', 2022, 35000),
    ('더 뉴 그랜저 IG', 2021, 50000),
    ('K5 3세대', 2022, 30000),
    ('쏘나타 (DN8)', 2022, 40000),
    ('카니발 4세대', 2022, 45000),
    ('싼타페 (MX5)', 2023, 30000),
]

for model_name, year, mileage in test_cases:
    pred = predict_price(model_name, year, mileage)
    
    # 실제 평균
    actual_df = df[(df['Model']==model_name) & (df['YearOnly']==year) & 
                   (df['Mileage']>=mileage-15000) & (df['Mileage']<=mileage+15000)]
    actual = actual_df['Price'].mean() if len(actual_df) > 0 else 0
    
    if actual > 0:
        error = abs(pred - actual) / actual * 100
        status = "✅" if error < 15 else ("⚠️" if error < 25 else "❌")
        print(f"{status} {model_name} {year}년 {mileage//10000}만km: 예측 {pred:,.0f}만원 / 실제 {actual:,.0f}만원 (오차 {error:.1f}%)")
    else:
        print(f"   {model_name} {year}년: 예측 {pred:,.0f}만원 (비교 데이터 없음)")

print("\n" + "="*70)
print("✅ V2 모델 학습 완료!")
print("="*70)
