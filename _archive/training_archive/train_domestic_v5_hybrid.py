"""
V5 하이브리드: V2 구조 + 옵션/연식/주행 단조제약
- Target Encoding으로 정확도 유지
- 핵심 피처에만 단조제약으로 논리성 보장
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
print("🚗 V5 하이브리드: Target Encoding + 선택적 단조제약")
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

# ========== 피처 ==========
# MSRP 
df['MSRP'] = df['Model'].apply(lambda x: get_msrp(x, False))

# 세그먼트
def get_seg(m):
    m = str(m).lower()
    if any(x in m for x in ['모닝','스파크','레이']): return 1
    if any(x in m for x in ['아반떼','k3']): return 2
    if any(x in m for x in ['쏘나타','k5']): return 3
    if any(x in m for x in ['그랜저','k7','k8']): return 4
    if any(x in m for x in ['k9','g70']): return 5
    if any(x in m for x in ['g80','gv80']): return 6
    if any(x in m for x in ['g90']): return 7
    if any(x in m for x in ['투싼','스포티지','셀토스']): return 3
    if any(x in m for x in ['싼타페','쏘렌토']): return 4
    if any(x in m for x in ['팰리세이드','모하비','gv70']): return 5
    return 3
df['Segment'] = df['Model'].apply(get_seg)

# 주행거리 구간
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)

# Target Encoding (핵심!)
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']

model_enc = df.groupby('Model')['Price'].mean()
model_year_enc = df.groupby('Model_Year')['Price'].mean()
model_year_mg_enc = df.groupby('Model_Year_MG')['Price'].mean()

df['Model_enc'] = df['Model'].map(model_enc).fillna(df['Price'].mean())
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])

# 연식/주행 피처
df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])

# 옵션
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0) if c in df.columns else 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)
df['Opt_Premium'] = df['has_sunroof']*3 + df['has_leather_seat']*2 + df['has_ventilated_seat']*3 + df['has_led_lamp']*2

print("✓ 피처 완료")

# ========== Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# ========== 피처 정의 ==========
features = [
    # Target Encoding (정확도 핵심) - 단조제약 없음
    'Model_enc',           # 0
    'Model_Year_enc',      # 0  
    'Model_Year_MG_enc',   # 0
    # MSRP (단조 증가)
    'MSRP',                # 1 ↑
    'Segment',             # 1 ↑
    # 연식/주행 (단조 감소)
    'Age',                 # -1 ↓
    'Age_log',             # -1 ↓
    'Mileage',             # -1 ↓
    'Mile_log',            # -1 ↓
    'Km_per_Year',         # -1 ↓
    # 옵션 (단조 증가) - 핵심!
    'Opt_Count',           # 1 ↑
    'Opt_Premium',         # 1 ↑
    'has_sunroof',         # 1 ↑
    'has_leather_seat',    # 1 ↑
    'has_led_lamp',        # 1 ↑
    'has_smart_key',       # 1 ↑
]

# 단조제약: Target Encoding은 자유, 나머지는 제약
mono = (0,0,0, 1,1, -1,-1,-1,-1,-1, 1,1,1,1,1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Price'])
X_test = test_df[features]
y_test = np.log1p(test_df['Price'])

print(f"✓ 피처: {len(features)}개")
print(f"✓ 단조제약: Target Encoding 3개 자유, 나머지 13개 제약")

# ========== 학습 ==========
print("\n🔥 학습 중...")
model = xgb.XGBRegressor(
    n_estimators=800,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    monotone_constraints=mono,
    early_stopping_rounds=50,
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
print(f"✓ MAPE: {mape:.1f}%")

errors = np.abs(actual - pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:10]:
    print(f"   {f}: {i:.3f}")

# ========== 저장 ==========
joblib.dump(model, 'models/domestic_v5.pkl')
joblib.dump(features, 'models/domestic_v5_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
}, 'models/domestic_v5_encoders.pkl')

# ========== 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v5(name, year, mileage, opts=None):
    age = 2025 - year
    mg = get_mg(mileage)
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    
    f = {
        'Model_enc': model_enc.get(name, 2500),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, 2500)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, 2500)),
        'MSRP': get_msrp(name, False),
        'Segment': get_seg(name),
        'Age': age, 'Age_log': np.log1p(age),
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage / (age + 1),
        'Opt_Count': 0, 'Opt_Premium': 0,
        'has_sunroof': 0, 'has_leather_seat': 0, 'has_led_lamp': 0, 'has_smart_key': 0
    }
    if opts:
        f.update(opts)
        f['Opt_Count'] = sum(opts.get(c,0) for c in opt_cols[:4])
        f['Opt_Premium'] = opts.get('has_sunroof',0)*3 + opts.get('has_leather_seat',0)*2 + opts.get('has_led_lamp',0)*2
    return np.expm1(model.predict(pd.DataFrame([f])[features])[0])

print("\n1️⃣ 동일조건 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    p = predict_v5(name, 2022, 30000, {'has_smart_key':1})
    st = "✅" if p >= prev else "⚠️역전"
    print(f"   {name:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt = predict_v5('더 뉴 그랜저 IG', 2022, 30000, {})
full_opt = predict_v5('더 뉴 그랜저 IG', 2022, 30000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
diff = full_opt - no_opt
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: {'+' if diff>0 else ''}{diff:,.0f}만원 {'✅정상!' if diff>0 else '❌버그'}")

print("\n3️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av = predict_v5('아반떼 (CN7)', 2024, 10000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so = predict_v5('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈 (정상)' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n4️⃣ 주행거리 효과 (그랜저 2022년):")
print("-"*60)
for km in [10000, 30000, 50000, 80000, 120000]:
    p = predict_v5('더 뉴 그랜저 IG', 2022, km, {'has_smart_key':1})
    print(f"   {km:,}km: {p:,.0f}만원")

print("\n5️⃣ 연식 효과 (그랜저 3만km):")
print("-"*60)
for year in [2019, 2020, 2021, 2022, 2023, 2024]:
    p = predict_v5('더 뉴 그랜저 IG', year, 30000, {'has_smart_key':1})
    print(f"   {year}년: {p:,.0f}만원")

print("\n" + "="*70)
print("✅ V5 완료!")
print("="*70)
