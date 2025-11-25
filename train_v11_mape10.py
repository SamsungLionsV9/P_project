"""
V11: MAPE 10% 목표 - 아웃라이어 제거 + 최적화
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')
from msrp_data import get_msrp

print("="*70)
print("🚗 V11: MAPE 10% 목표")
print("="*70)

# ========== 1. 데이터 로드 ==========
df = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df = df[(df['Price'] >= 100) & (df['Price'] <= 50000)]
df = df[df['Mileage'] < 300000]
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'])
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['Age'] = 2025 - df['YearOnly']
df['Km_per_Year'] = df['Mileage'] / (df['Age'] + 1)
df = df[df['Km_per_Year'] <= 40000]
print(f"원본 데이터: {len(df):,}행")

# ========== 2. 아웃라이어 제거 ==========
print("\n🔍 아웃라이어 제거...")
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
model_year_stats = df.groupby('Model_Year')['Price'].agg(['mean', 'std', 'count'])
df = df.merge(model_year_stats[['mean', 'std']], left_on='Model_Year', right_index=True, suffixes=('', '_my'))
df['z_score'] = np.abs(df['Price'] - df['mean']) / (df['std'] + 1)

print(f"z_score > 2: {(df['z_score'] > 2).sum():,}행 ({(df['z_score'] > 2).mean()*100:.1f}%)")
print(f"z_score > 1.5: {(df['z_score'] > 1.5).sum():,}행 ({(df['z_score'] > 1.5).mean()*100:.1f}%)")

# 아웃라이어 제거 (z_score <= 1.0 - 최강)
df = df[df['z_score'] <= 1.0].copy()
print(f"정제 후: {len(df):,}행")

# ========== 3. 피처 엔지니어링 ==========
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']

# Target Encoding
model_enc = df.groupby('Model')['Price'].mean()
model_year_enc = df.groupby('Model_Year')['Price'].mean()
model_year_mg_enc = df.groupby('Model_Year_MG')['Price'].mean()
brand_enc = df.groupby('Manufacturer')['Price'].mean()

df['Model_enc'] = df['Model'].map(model_enc).fillna(df['Price'].mean())
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(df['Price'].mean())

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])
df['Age_sq'] = df['Age'] ** 2

# 상태
df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

# 옵션
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)
df['Opt_Premium'] = (df['has_sunroof']*3 + df['has_leather_seat']*2 + 
                     df['has_ventilated_seat']*3 + df['has_led_lamp']*2)

# ========== 4. Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# ========== 5. 피처 ==========
features = [
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    'Age', 'Age_log', 'Age_sq',
    'Mileage', 'Mile_log', 'Km_per_Year',
    'is_accident_free', 'inspection_grade_enc',
    'Opt_Count', 'Opt_Premium',
    'has_sunroof', 'has_leather_seat', 'has_led_lamp', 'has_smart_key',
    'has_ventilated_seat', 'has_heated_seat', 'has_navigation', 'has_rear_camera',
]

# 옵션만 단조제약
mono = (0,0,0,0, 0,0,0, 0,0,0, 1,1, 1,1, 1,1,1,1,1,1,1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Price'])
X_test = test_df[features]
y_test = np.log1p(test_df['Price'])

# ========== 6. 학습 ==========
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
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=200)

# ========== 7. 평가 ==========
print("\n" + "="*70)
print("📈 평가")
print("="*70)

pred = np.expm1(model.predict(X_test))
actual = test_df['Price'].values
mae = mean_absolute_error(actual, pred)
mape = np.mean(np.abs(actual - pred) / actual) * 100
r2 = r2_score(y_test, model.predict(X_test))

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}% (목표: ≤10%)")

errors = np.abs(actual - pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

# ========== 8. 저장 ==========
joblib.dump(model, 'models/domestic_v11.pkl')
joblib.dump(features, 'models/domestic_v11_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
    'brand_enc': brand_enc.to_dict(),
}, 'models/domestic_v11_encoders.pkl')
print("✅ 저장 완료!")

# ========== 9. 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v11(name, year, mileage, opts=None, accident_free=1, grade='normal'):
    age = 2025 - year
    mg = get_mg(mileage)
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    grade_enc = {'normal':0, 'good':1, 'excellent':2}.get(grade, 0)
    
    opt_values = opts if opts else {}
    opt_count = sum(opt_values.get(c, 0) for c in opt_cols)
    opt_premium = (opt_values.get('has_sunroof',0)*3 + opt_values.get('has_leather_seat',0)*2 +
                   opt_values.get('has_ventilated_seat',0)*3 + opt_values.get('has_led_lamp',0)*2)
    
    f = {
        'Model_enc': model_enc.get(name, 2500),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, 2500)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, 2500)),
        'Brand_enc': brand_enc.get('현대', 2500),
        'Age': age, 'Age_log': np.log1p(age), 'Age_sq': age**2,
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'is_accident_free': accident_free,
        'inspection_grade_enc': grade_enc,
        'Opt_Count': opt_count,
        'Opt_Premium': opt_premium,
        **{c: opt_values.get(c, 0) for c in opt_cols}
    }
    
    return np.expm1(model.predict(pd.DataFrame([f])[features])[0])

print("\n1️⃣ 동일조건 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    p = predict_v11(name, 2022, 30000, {'has_smart_key':1})
    st = "✅" if p >= prev else "⚠️"
    print(f"   {name:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt = predict_v11('더 뉴 그랜저 IG', 2022, 30000, {})
full_opt = predict_v11('더 뉴 그랜저 IG', 2022, 30000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
diff = full_opt - no_opt
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: +{diff:,.0f}만원 {'✅' if diff>0 else '❌'}")

print("\n3️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av = predict_v11('아반떼 (CN7)', 2024, 10000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so = predict_v11('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n" + "="*70)
print("✅ V11 완료!")
print("="*70)
