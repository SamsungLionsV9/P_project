"""
외제차 V14: FuelType 추가 학습
==============================
V13 기반 + FuelType 피처 추가
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("🚗 외제차 V14: FuelType 포함 학습")
print("="*70)

# ========== 1. 데이터 로드 ==========
df = pd.read_csv('../../data/encar_imported_data.csv')
df_detail = pd.read_csv('../../data/complete_imported_details.csv')
df = df.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model', 'FuelType'])

# 이상치 필터링 (가격) - 외제차는 상한 높음
PRICE_MIN = 100       # 100만원 이상
PRICE_MAX = 100000    # 10억 이하 (외제차 고가 모델 포함)
SPECIAL_PRICES = {9999, 8888, 7777, 6666, 5555, 1111, 10000, 1234, 4321}  # 특수 가격

df = df[(df['Price'] >= PRICE_MIN) & (df['Price'] <= PRICE_MAX)]
df = df[~df['Price'].isin(SPECIAL_PRICES)]  # 특수 가격 제거 (가격 미정 등)
df = df[df['Mileage'] < 300000]
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'])
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['Age'] = 2025 - df['YearOnly']
df['Km_per_Year'] = df['Mileage'] / (df['Age'] + 1)
df = df[df['Km_per_Year'] <= 50000]
print(f"원본 데이터: {len(df):,}행")

# ========== 2. FuelType 처리 ==========
print("\n⛽ FuelType 처리...")
def normalize_fuel(f):
    f = str(f).lower()
    if '하이브리드' in f or '전기' in f or 'hybrid' in f or 'electric' in f:
        return '하이브리드'
    elif '디젤' in f or 'diesel' in f:
        return '디젤'
    else:
        return '가솔린'

df['Fuel'] = df['FuelType'].apply(normalize_fuel)
fuel_dist = df['Fuel'].value_counts()
print("연료 분포:")
for fuel, cnt in fuel_dist.items():
    print(f"   {fuel}: {cnt:,}개 ({cnt/len(df)*100:.1f}%)")

# ========== 3. 옵션 프리미엄 ==========
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0

OPTION_PREMIUM = {
    'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
    'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
    'has_smart_key': 50, 'has_rear_camera': 50,
}
df['Option_Premium'] = sum(df[c] * OPTION_PREMIUM[c] for c in opt_cols)
df['Base_Price'] = (df['Price'] - df['Option_Premium']).clip(lower=100)

# ========== 4. 브랜드 등급 ==========
BRAND_TIER = {
    '페라리': 6, '람보르기니': 6, '맥라렌': 6, '롤스로이스': 6, '벤틀리': 6,
    '포르쉐': 5, '마세라티': 5,
    '벤츠': 4, 'BMW': 4, '아우디': 4, '렉서스': 4, '테슬라': 4,
    '볼보': 3, '랜드로버': 3, '재규어': 3, '인피니티': 3, '캐딜락': 3,
    '폭스바겐': 2, '미니': 2, '지프': 2, '푸조': 2, '시트로엥': 2,
    '토요타': 3, '혼다': 3, '닛산': 2, '마쓰다': 2,
}
df['Brand_Tier'] = df['Manufacturer'].map(BRAND_TIER).fillna(2)

# ========== 5. 클래스 추출 ==========
CLASS_RANK = {
    'A': 1, 'B': 1, 'CLA': 2, 'C': 2, 'E': 3, 'S': 4, 'G': 5,
    'GLA': 2, 'GLB': 2, 'GLC': 3, 'GLE': 3, 'GLS': 4, 'EQS': 4, 'EQE': 3,
    '1시리즈': 1, '2시리즈': 1, '3시리즈': 2, '4시리즈': 2, '5시리즈': 3, '7시리즈': 4,
    'X1': 2, 'X2': 2, 'X3': 3, 'X4': 3, 'X5': 4, 'X6': 4, 'X7': 5,
    'A1': 1, 'A3': 1, 'A4': 2, 'A5': 2, 'A6': 3, 'A7': 3, 'A8': 4,
    'Q2': 1, 'Q3': 2, 'Q5': 3, 'Q7': 4, 'Q8': 4,
    '911': 4, 'Cayenne': 4, 'Macan': 3, 'Taycan': 4,
    'Model 3': 3, 'Model Y': 3, 'Model S': 4, 'Model X': 4,
    'S60': 2, 'S90': 3, 'XC40': 2, 'XC60': 3, 'XC90': 4,
}

def extract_class(model, manufacturer):
    model = str(model)
    mfr = str(manufacturer).lower()
    
    if '벤츠' in mfr:
        match = re.search(r'([A-Z])-?클래스|([A-Z])-?Class', model, re.I)
        if match:
            cls = (match.group(1) or match.group(2)).upper()
            return cls, CLASS_RANK.get(cls, 3)
        match = re.search(r'(GL[ABCES]|EQ[SE])', model, re.I)
        if match:
            return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
    
    if 'bmw' in mfr:
        match = re.search(r'(\d)시리즈', model)
        if match:
            cls = f"{match.group(1)}시리즈"
            return cls, CLASS_RANK.get(cls, 3)
        match = re.search(r'\b([XMi]\d)\b', model)
        if match:
            return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
    
    if '아우디' in mfr:
        match = re.search(r'\b(A\d|Q\d|RS\d)', model, re.I)
        if match:
            return match.group(1).upper(), CLASS_RANK.get(match.group(1).upper(), 3)
    
    clean = re.sub(r'\([^)]*\)', '', model).strip()
    first = clean.split()[0] if clean else model
    return first if len(first) > 1 else 'Unknown', 3

df['Class'], df['Class_Rank'] = zip(*df.apply(lambda r: extract_class(r['Model'], r['Manufacturer']), axis=1))

# ========== 6. 아웃라이어 제거 ==========
print("\n🔍 아웃라이어 제거...")
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
model_year_stats = df.groupby('Model_Year')['Base_Price'].agg(['mean', 'std', 'count'])
df = df.merge(model_year_stats[['mean', 'std']], left_on='Model_Year', right_index=True, suffixes=('', '_my'))
df['z_score'] = np.abs(df['Base_Price'] - df['mean']) / (df['std'] + 1)
df = df[df['z_score'] <= 1.0].copy()
print(f"정제 후: {len(df):,}행")

# ========== 7. Target Encoding ==========
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']
df['Class_Year'] = df['Class'] + '_' + df['YearOnly'].astype(str)

def smooth_enc(df, col, target, min_n=30):
    g_mean = df[target].mean()
    stats = df.groupby(col)[target].agg(['mean', 'count'])
    return ((stats['mean'] * stats['count'] + g_mean * min_n) / (stats['count'] + min_n)).to_dict(), g_mean

model_enc, global_mean = smooth_enc(df, 'Model', 'Base_Price', 50)
model_year_enc, _ = smooth_enc(df, 'Model_Year', 'Base_Price', 30)
model_year_mg_enc, _ = smooth_enc(df, 'Model_Year_MG', 'Base_Price', 20)
brand_enc, _ = smooth_enc(df, 'Manufacturer', 'Base_Price', 100)
class_enc, _ = smooth_enc(df, 'Class', 'Base_Price', 30)
class_year_enc, _ = smooth_enc(df, 'Class_Year', 'Base_Price', 20)
fuel_enc, _ = smooth_enc(df, 'Fuel', 'Base_Price', 50)  # 연료 인코딩!

df['Model_enc'] = df['Model'].map(model_enc).fillna(global_mean)
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(global_mean)
df['Class_enc'] = df['Class'].map(class_enc).fillna(global_mean)
df['Class_Year_enc'] = df['Class_Year'].map(class_year_enc).fillna(df['Class_enc'])
df['Fuel_enc'] = df['Fuel'].map(fuel_enc).fillna(global_mean)  # 연료 인코딩!

# 연료 원핫
df['is_diesel'] = (df['Fuel'] == '디젤').astype(int)
df['is_hybrid'] = (df['Fuel'] == '하이브리드').astype(int)

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])

df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

# ========== 8. Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"\n✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 9. 피처 (FuelType 추가!) ==========
features = [
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc', 
    'Class_enc', 'Class_Year_enc',
    'Fuel_enc', 'is_diesel', 'is_hybrid',  # 연료 피처 추가!
    'Brand_Tier', 'Class_Rank',
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
    'is_accident_free', 'inspection_grade_enc',
]

mono = (0,0,0,0, 0,0, 0,0,0, 1,1, 0,0,0,0,0, 1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Base_Price'])
X_test = test_df[features]

# ========== 10. 학습 ==========
print("\n🔥 학습...")
model = xgb.XGBRegressor(
    n_estimators=2000,
    max_depth=9,
    learning_rate=0.02,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    monotone_constraints=mono,
    early_stopping_rounds=100,
    random_state=42,
    verbosity=1
)
model.fit(X_train, y_train, eval_set=[(X_test, np.log1p(test_df['Base_Price']))], verbose=200)

# ========== 11. 평가 ==========
print("\n" + "="*70)
print("📈 평가")
print("="*70)

pred_base = np.expm1(model.predict(X_test))
pred_final = pred_base + test_df['Option_Premium'].values
actual = test_df['Price'].values

mae = mean_absolute_error(actual, pred_final)
mape = np.mean(np.abs(actual - pred_final) / actual) * 100
r2 = r2_score(np.log1p(actual), np.log1p(pred_final))

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}%")

errors = np.abs(actual - pred_final) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

print("\n⭐ Feature Importance (상위 15):")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:15]:
    print(f"   {f}: {i:.4f}")

# ========== 12. 저장 ==========
joblib.dump(model, '../../models/imported_v14.pkl')
joblib.dump(features, '../../models/imported_v14_features.pkl')
joblib.dump({
    'model_enc': model_enc,
    'model_year_enc': model_year_enc,
    'model_year_mg_enc': model_year_mg_enc,
    'brand_enc': brand_enc,
    'class_enc': class_enc,
    'class_year_enc': class_year_enc,
    'fuel_enc': fuel_enc,  # 연료 인코딩 저장!
    'global_mean': global_mean,
    'option_premiums': OPTION_PREMIUM,
}, '../../models/imported_v14_encoders.pkl')
print("✅ 저장 완료!")

# ========== 13. 테스트 ==========
print("\n" + "="*70)
print("🧪 연료별 테스트")
print("="*70)

def predict_v14(name, brand, year, mileage, fuel='가솔린', opts=None):
    age = 2025 - year
    mg = get_mg(mileage)
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    cls, cls_rank = extract_class(name, brand)
    cls_year = f"{cls}_{year}"
    
    f = {
        'Model_enc': model_enc.get(name, global_mean),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, global_mean)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, global_mean)),
        'Brand_enc': brand_enc.get(brand, global_mean),
        'Class_enc': class_enc.get(cls, global_mean),
        'Class_Year_enc': class_year_enc.get(cls_year, class_enc.get(cls, global_mean)),
        'Fuel_enc': fuel_enc.get(fuel, global_mean),
        'is_diesel': 1 if fuel == '디젤' else 0,
        'is_hybrid': 1 if fuel == '하이브리드' else 0,
        'Brand_Tier': BRAND_TIER.get(brand, 3),
        'Class_Rank': cls_rank,
        'Age': age, 'Age_log': np.log1p(age),
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'is_accident_free': 1,
        'inspection_grade_enc': 0,
    }
    
    base_price = np.expm1(model.predict(pd.DataFrame([f])[features])[0])
    opt_premium = sum(opts.get(c, 0) * OPTION_PREMIUM[c] for c in opt_cols) if opts else 0
    return base_price + opt_premium

print("\n1️⃣ 연료별 가격 비교 (E-클래스 2022년 3만km):")
print("-"*60)
base = predict_v14('E-클래스 W214', '벤츠', 2022, 30000, '가솔린')
for fuel in ['가솔린', '디젤', '하이브리드']:
    p = predict_v14('E-클래스 W214', '벤츠', 2022, 30000, fuel)
    diff = p - base
    print(f"   {fuel:10}: {p:,.0f}만원 ({diff:+,.0f})")

print("\n" + "="*70)
print("✅ V14 완료!")
print("="*70)
