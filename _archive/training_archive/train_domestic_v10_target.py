"""
V10: V2 정확도 + 옵션 단조제약 + 설명 가능
==========================================
목표: MAPE ≤ 10%, 옵션 효과 정방향
전략: V2처럼 전체 Price 예측 + 옵션에 단조제약
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
print("🚗 V10: V2 정확도 + 옵션 단조제약")
print("="*70)

# ========== 데이터 ==========
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
print(f"✓ 데이터: {len(df):,}행")

# ========== 피처 (V2 스타일) ==========
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)

df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']

# Target Encoding (원본 V2 방식 - 스무딩 없이 빠른 수렴)
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

# 무사고, 검사등급
df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

# 옵션 (개별 피처로)
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0

# 옵션 집계
df['Opt_Count'] = sum(df[c] for c in opt_cols)
df['Opt_Premium'] = (df['has_sunroof']*3 + df['has_leather_seat']*2 + 
                     df['has_ventilated_seat']*3 + df['has_led_lamp']*2)

# ========== Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# ========== 피처 정의 ==========
# 피처 순서: [Target Encoding] [연속형] [사고/검사] [옵션]
features = [
    # Target Encoding (자유 - 가장 강력한 예측력)
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    # 연속형
    'Age', 'Age_log', 'Age_sq',
    'Mileage', 'Mile_log', 'Km_per_Year',
    # 상태
    'is_accident_free', 'inspection_grade_enc',
    # 옵션 (단조제약!)
    'Opt_Count', 'Opt_Premium',
    'has_sunroof', 'has_leather_seat', 'has_led_lamp', 'has_smart_key',
    'has_ventilated_seat', 'has_heated_seat', 'has_navigation', 'has_rear_camera',
]

# 단조제약: 옵션만 증가 제약, 나머지는 자유롭게 학습
mono = (
    0,0,0,0,  # Target Encoding: 자유
    0,0,0,    # Age: 자유 (비선형 관계 학습)
    0,0,0,    # Mileage: 자유
    1,1,      # 사고/검사: 증가
    1,1,      # 옵션 집계: 증가
    1,1,1,1,1,1,1,1,  # 개별 옵션: 증가
)

X_train = train_df[features]
y_train = np.log1p(train_df['Price'])
X_test = test_df[features]
y_test = np.log1p(test_df['Price'])

print(f"✓ 피처: {len(features)}개")

# ========== 학습 ==========
print("\n🔥 학습 중...")
model = xgb.XGBRegressor(
    n_estimators=1500,
    max_depth=8,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    reg_alpha=0.1,
    reg_lambda=1.0,
    monotone_constraints=mono,
    early_stopping_rounds=100,
    random_state=42,
    verbosity=1
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=100)

# ========== 평가 ==========
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

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:12]:
    print(f"   {f}: {i:.4f}")

# ========== 저장 ==========
joblib.dump(model, 'models/domestic_v10.pkl')
joblib.dump(features, 'models/domestic_v10_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
    'brand_enc': brand_enc.to_dict(),
}, 'models/domestic_v10_encoders.pkl')
print("✅ 저장 완료!")

# ========== 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v10(name, year, mileage, opts=None, accident_free=1, grade='normal'):
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
        'has_sunroof': opt_values.get('has_sunroof', 0),
        'has_leather_seat': opt_values.get('has_leather_seat', 0),
        'has_led_lamp': opt_values.get('has_led_lamp', 0),
        'has_smart_key': opt_values.get('has_smart_key', 0),
        'has_ventilated_seat': opt_values.get('has_ventilated_seat', 0),
        'has_heated_seat': opt_values.get('has_heated_seat', 0),
        'has_navigation': opt_values.get('has_navigation', 0),
        'has_rear_camera': opt_values.get('has_rear_camera', 0),
    }
    
    return np.expm1(model.predict(pd.DataFrame([f])[features])[0])

print("\n1️⃣ 동일조건 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    p = predict_v10(name, 2022, 30000, {'has_smart_key':1})
    st = "✅" if p >= prev else "⚠️"
    print(f"   {name:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt = predict_v10('더 뉴 그랜저 IG', 2022, 30000, {})
full_opt = predict_v10('더 뉴 그랜저 IG', 2022, 30000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
diff = full_opt - no_opt
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: {'+' if diff>0 else ''}{diff:,.0f}만원 {'✅' if diff>0 else '❌'}")

print("\n3️⃣ 무사고 효과:")
print("-"*60)
acc = predict_v10('더 뉴 그랜저 IG', 2022, 30000, {}, accident_free=0)
no_acc = predict_v10('더 뉴 그랜저 IG', 2022, 30000, {}, accident_free=1)
print(f"   사고차: {acc:,.0f}만원")
print(f"   무사고: {no_acc:,.0f}만원")
print(f"   차이: +{no_acc-acc:,.0f}만원 {'✅' if no_acc>acc else '❌'}")

print("\n4️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av = predict_v10('아반떼 (CN7)', 2024, 10000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so = predict_v10('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n5️⃣ 개별 옵션 효과:")
print("-"*60)
base = predict_v10('더 뉴 그랜저 IG', 2022, 30000, {})
for opt in opt_cols:
    with_opt = predict_v10('더 뉴 그랜저 IG', 2022, 30000, {opt: 1})
    diff = with_opt - base
    print(f"   {opt:20}: {'+' if diff>=0 else ''}{diff:,.0f}만원 {'✅' if diff>=0 else '❌'}")

print("\n" + "="*70)
print("✅ V10 완료!")
print("="*70)
