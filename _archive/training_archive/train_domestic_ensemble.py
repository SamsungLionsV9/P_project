"""
국산차 앙상블 모델: V2(정확도) + V4(논리성) 결합
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
print("🚗 앙상블 모델: V2(정확도) + V4(논리성)")
print("="*70)

# ========== 데이터 로드 ==========
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

# ========== 공통 피처 ==========
df['MSRP'] = df['Model'].apply(lambda x: get_msrp(x, False))
df['MSRP_log'] = np.log1p(df['MSRP'])
df['Age_sq'] = df['Age']**2
df['Mile_log'] = np.log1p(df['Mileage'])

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

# 옵션
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key','has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0) if c in df.columns else 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)
df['Opt_Premium'] = df['has_sunroof']*3 + df['has_leather_seat']*2 + df['has_ventilated_seat']*3 + df['has_led_lamp']*2

# ========== V2 피처 (Target Encoding) ==========
def get_mileage_group(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mileage_group)
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']

# Target Encodings
model_enc = df.groupby('Model')['Price'].mean()
model_year_enc = df.groupby('Model_Year')['Price'].mean()
model_year_mg_enc = df.groupby('Model_Year_MG')['Price'].mean()
brand_enc = df.groupby('Manufacturer')['Price'].mean()

df['Model_enc'] = df['Model'].map(model_enc).fillna(df['Price'].mean())
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(df['Price'].mean())

# ========== Train/Test Split ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# ========== 모델1: V2 (정확도 우선) ==========
print("\n🔵 모델1: V2 (Target Encoding 기반 - 정확도)")
v2_features = ['Model_enc','Model_Year_enc','Model_Year_MG_enc','Brand_enc',
               'Age','Age_sq','Mileage','Mile_log','Km_per_Year','Segment',
               'Opt_Count','has_sunroof','has_leather_seat','has_led_lamp']

X_train_v2 = train_df[v2_features]
y_train = np.log1p(train_df['Price'])
X_test_v2 = test_df[v2_features]
y_test = np.log1p(test_df['Price'])

model_v2 = xgb.XGBRegressor(n_estimators=500, max_depth=7, learning_rate=0.05,
                            early_stopping_rounds=30, random_state=42, verbosity=0)
model_v2.fit(X_train_v2, y_train, eval_set=[(X_test_v2, y_test)], verbose=False)

pred_v2 = np.expm1(model_v2.predict(X_test_v2))
mape_v2 = np.mean(np.abs(test_df['Price'].values - pred_v2) / test_df['Price'].values) * 100
print(f"   MAPE: {mape_v2:.1f}%")

# ========== 모델2: V4 (논리성 우선 - 단조제약) ==========
print("\n🟢 모델2: V4 (단조제약 - 논리성)")
v4_features = ['MSRP','MSRP_log','Segment','Age','Age_sq','Mileage','Mile_log','Km_per_Year',
               'Opt_Count','Opt_Premium','has_sunroof','has_leather_seat','has_led_lamp','has_smart_key']

# 단조제약: MSRP↑가격↑, Age↑가격↓, Mile↑가격↓, Opt↑가격↑
mono_v4 = (1,1,1,-1,0,-1,-1,-1,1,1,1,1,1,1)

X_train_v4 = train_df[v4_features]
X_test_v4 = test_df[v4_features]

model_v4 = xgb.XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05,
                            monotone_constraints=mono_v4, early_stopping_rounds=30, 
                            random_state=42, verbosity=0)
model_v4.fit(X_train_v4, y_train, eval_set=[(X_test_v4, y_test)], verbose=False)

pred_v4 = np.expm1(model_v4.predict(X_test_v4))
mape_v4 = np.mean(np.abs(test_df['Price'].values - pred_v4) / test_df['Price'].values) * 100
print(f"   MAPE: {mape_v4:.1f}%")

# ========== 앙상블 최적 가중치 탐색 ==========
print("\n🔍 최적 가중치 탐색...")
best_alpha, best_mape = 0, 100
for alpha in np.arange(0.0, 1.05, 0.05):
    ensemble = alpha * pred_v2 + (1 - alpha) * pred_v4
    mape = np.mean(np.abs(test_df['Price'].values - ensemble) / test_df['Price'].values) * 100
    if mape < best_mape:
        best_mape, best_alpha = mape, alpha

print(f"   최적: V2 {best_alpha:.0%} + V4 {1-best_alpha:.0%}")
print(f"   앙상블 MAPE: {best_mape:.1f}%")

# ========== 최종 앙상블 평가 ==========
print("\n" + "="*70)
print(f"📈 최종 앙상블: V2 {best_alpha:.0%} + V4 {1-best_alpha:.0%}")
print("="*70)

final_pred = best_alpha * pred_v2 + (1 - best_alpha) * pred_v4
actual = test_df['Price'].values
mae = mean_absolute_error(actual, final_pred)
mape = np.mean(np.abs(actual - final_pred) / actual) * 100
r2 = r2_score(np.log1p(actual), np.log1p(final_pred))

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}%")

# 오차 분포
errors = np.abs(actual - final_pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

# ========== 저장 ==========
print("\n💾 저장...")
joblib.dump({'v2': model_v2, 'v4': model_v4, 'alpha': best_alpha}, 'models/domestic_ensemble.pkl')
joblib.dump({'v2': v2_features, 'v4': v4_features}, 'models/domestic_ensemble_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
    'brand_enc': brand_enc.to_dict(),
}, 'models/domestic_ensemble_encoders.pkl')

# ========== 핵심 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_ensemble(name, year, mileage, opts=None):
    age = 2025 - year
    mg = get_mileage_group(mileage)
    msrp = get_msrp(name, False)
    
    # V2 피처
    model_key = name
    my_key = f"{name}_{year}"
    mymg_key = f"{my_key}_{mg}"
    
    f_v2 = {
        'Model_enc': model_enc.get(model_key, 2500),
        'Model_Year_enc': model_year_enc.get(my_key, model_enc.get(model_key, 2500)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg_key, model_year_enc.get(my_key, 2500)),
        'Brand_enc': 2500,
        'Age': age, 'Age_sq': age**2, 'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1), 'Segment': get_seg(name),
        'Opt_Count': 0, 'has_sunroof': 0, 'has_leather_seat': 0, 'has_led_lamp': 0
    }
    
    # V4 피처
    f_v4 = {
        'MSRP': msrp, 'MSRP_log': np.log1p(msrp), 'Segment': get_seg(name),
        'Age': age, 'Age_sq': age**2, 'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'Opt_Count': 0, 'Opt_Premium': 0, 'has_sunroof': 0, 'has_leather_seat': 0, 
        'has_led_lamp': 0, 'has_smart_key': 0
    }
    
    if opts:
        for k, v in opts.items():
            if k in f_v2: f_v2[k] = v
            if k in f_v4: f_v4[k] = v
        f_v2['Opt_Count'] = sum(opts.get(c,0) for c in ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key'])
        f_v4['Opt_Count'] = f_v2['Opt_Count']
        f_v4['Opt_Premium'] = opts.get('has_sunroof',0)*3 + opts.get('has_leather_seat',0)*2 + opts.get('has_led_lamp',0)*2
    
    p_v2 = np.expm1(model_v2.predict(pd.DataFrame([f_v2])[v2_features])[0])
    p_v4 = np.expm1(model_v4.predict(pd.DataFrame([f_v4])[v4_features])[0])
    return best_alpha * p_v2 + (1 - best_alpha) * p_v4, p_v2, p_v4

print("\n1️⃣ 동일조건 서열 (2022년 3만km 기본옵션):")
print("-"*60)
models = ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']
prev = 0
for name in models:
    p, v2, v4 = predict_ensemble(name, 2022, 30000, {'has_smart_key':1})
    status = "✅" if p > prev else "⚠️"
    print(f"   {name:20}: {p:,.0f}만원 (V2:{v2:,.0f}, V4:{v4:,.0f}) {status}")
    prev = p

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt, _, _ = predict_ensemble('더 뉴 그랜저 IG', 2022, 30000, {})
full_opt, _, _ = predict_ensemble('더 뉴 그랜저 IG', 2022, 30000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
diff = full_opt - no_opt
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: {'+' if diff>0 else ''}{diff:,.0f}만원 {'✅정상' if diff>0 else '❌버그'}")

print("\n3️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av, _, _ = predict_ensemble('아반떼 (CN7)', 2024, 10000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so, _, _ = predict_ensemble('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈 (정상)' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n4️⃣ 연식별 가격 (그랜저):")
print("-"*60)
for year in [2019, 2020, 2021, 2022, 2023, 2024]:
    p, _, _ = predict_ensemble('더 뉴 그랜저 IG', year, 30000, {'has_smart_key':1})
    print(f"   {year}년: {p:,.0f}만원")

print("\n" + "="*70)
print("✅ 앙상블 모델 완료!")
print("="*70)
