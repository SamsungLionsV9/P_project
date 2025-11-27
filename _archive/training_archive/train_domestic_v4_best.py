"""
국산차 V4 - Best Practice: 단조제약 + 피처분리
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
print("🚗 V4 - Best Practice (단조제약 + 피처분리)")
print("="*70)

# 1. 데이터 로드 & 전처리
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
df = df[(df['Km_per_Year'] <= 40000)]
print(f"✓ 데이터: {len(df):,}행")

# 2. 피처 엔지니어링
df['Base_Model_Price'] = df['Model'].apply(lambda x: get_msrp(x, False))
df['Base_Price_log'] = np.log1p(df['Base_Model_Price'])

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
    if any(x in m for x in ['카니발','스타리아']): return 4
    return 3
df['Segment'] = df['Model'].apply(get_seg)

# 순수 모델 평균 (연식/주행 제외)
model_mean = df.groupby('Model')['Price'].mean().to_dict()
df['Model_avg'] = df['Model'].map(model_mean).fillna(df['Price'].mean())

df['Age_sq'] = df['Age']**2
df['Mile_log'] = np.log1p(df['Mileage'])

# 옵션
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key','has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    if c in df.columns: df[c] = df[c].fillna(0)
    else: df[c] = 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)
df['Opt_Premium'] = df['has_sunroof']*3 + df['has_leather_seat']*2 + df['has_ventilated_seat']*3 + df['has_led_lamp']*2 + df['has_smart_key']
print("✓ 피처 완료")

# 3. Train/Test
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
features = ['Base_Model_Price','Base_Price_log','Model_avg','Segment',
            'Age','Age_sq','Mileage','Mile_log','Km_per_Year',
            'Opt_Count','Opt_Premium','has_sunroof','has_leather_seat','has_led_lamp','has_smart_key']
X_train, y_train = train_df[features], np.log1p(train_df['Price'])
X_test, y_test = test_df[features], np.log1p(test_df['Price'])

# 4. 단조제약 (핵심!)
# 1=증가, -1=감소, 0=없음
mono = (1,1,1,1, -1,0,-1,-1,-1, 1,1,1,1,1,1)  # 순서대로
print(f"✓ 단조제약: MSRP↑가격↑, Age↑가격↓, Mileage↑가격↓, Option↑가격↑")

# 5. 학습
model = xgb.XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05,
                         monotone_constraints=mono, early_stopping_rounds=30, random_state=42)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=50)

# 6. 평가
pred = np.expm1(model.predict(X_test))
actual = test_df['Price'].values
mae = mean_absolute_error(actual, pred)
mape = np.mean(np.abs(actual-pred)/actual)*100
r2 = r2_score(y_test, model.predict(X_test))
print(f"\n📈 Test: R²={r2:.4f}, MAE={mae:.0f}만원, MAPE={mape:.1f}%")

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:8]:
    print(f"   {f}: {i:.3f}")

# 7. 저장
joblib.dump(model, 'models/domestic_v4.pkl')
joblib.dump(features, 'models/domestic_v4_features.pkl')
joblib.dump(model_mean, 'models/domestic_v4_model_enc.pkl')

# 8. 테스트
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict(name, year, km, opts=None):
    age = 2025 - year
    f = {'Base_Model_Price': get_msrp(name,False), 'Base_Price_log': np.log1p(get_msrp(name,False)),
         'Model_avg': model_mean.get(name, 2500), 'Segment': get_seg(name),
         'Age': age, 'Age_sq': age**2, 'Mileage': km, 'Mile_log': np.log1p(km), 'Km_per_Year': km/(age+1),
         'Opt_Count': 0, 'Opt_Premium': 0, 'has_sunroof': 0, 'has_leather_seat': 0, 'has_led_lamp': 0, 'has_smart_key': 0}
    if opts:
        f.update(opts)
        f['Opt_Count'] = sum(opts.get(c,0) for c in ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key'])
        f['Opt_Premium'] = opts.get('has_sunroof',0)*3 + opts.get('has_leather_seat',0)*2 + opts.get('has_led_lamp',0)*2
    return np.expm1(model.predict(pd.DataFrame([f])[features])[0])

print("\n1️⃣ 동일조건 서열 (2022년 3만km 기본옵션):")
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    p = predict(name, 2022, 30000, {'has_smart_key':1})
    print(f"   {name:20}: {p:,.0f}만원 (MSRP {get_msrp(name,False):,})")

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
no_opt = predict('더 뉴 그랜저 IG', 2022, 30000, {})
full_opt = predict('더 뉴 그랜저 IG', 2022, 30000, {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: +{full_opt-no_opt:,.0f}만원 ({'✅정상' if full_opt>no_opt else '❌버그'})")

print("\n3️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
av = predict('아반떼 (CN7)', 2024, 10000, {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so = predict('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈 (정상)' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n✅ V4 완료!")
