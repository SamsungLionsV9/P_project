"""
V6 최종: 기본가격 예측 + 옵션 프리미엄 별도 계산
==========================================
1단계: 모델+연식+주행거리로 기본가격 예측
2단계: 옵션별 프리미엄 테이블로 추가 계산
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
print("🚗 V6 최종: 기본가격 + 옵션 프리미엄 분리")
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

# ========== 옵션 프리미엄 분석 ==========
print("\n📊 옵션별 가격 차이 분석...")
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0) if c in df.columns else 0

# 옵션별 실제 가격 프리미엄 계산 (같은 Model_Year 그룹 내에서)
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
option_premiums = {}
for opt in opt_cols:
    # 옵션 있는 차 vs 없는 차 가격 차이
    with_opt = df[df[opt] == 1].groupby('Model_Year')['Price'].mean()
    without_opt = df[df[opt] == 0].groupby('Model_Year')['Price'].mean()
    common = with_opt.index.intersection(without_opt.index)
    if len(common) > 10:
        diff = (with_opt[common] - without_opt[common]).median()
        option_premiums[opt] = max(0, diff)  # 음수면 0으로
    else:
        option_premiums[opt] = 0

print("📈 옵션 프리미엄 (데이터 기반):")
for opt, premium in sorted(option_premiums.items(), key=lambda x: -x[1]):
    print(f"   {opt}: +{premium:.0f}만원")

# 최종 프리미엄 테이블 (데이터 + 도메인지식 보정)
OPTION_PREMIUM = {
    'has_sunroof': max(option_premiums.get('has_sunroof', 0), 50),        # 최소 50만원
    'has_leather_seat': max(option_premiums.get('has_leather_seat', 0), 30),  # 최소 30만원
    'has_ventilated_seat': max(option_premiums.get('has_ventilated_seat', 0), 40), # 최소 40만원
    'has_heated_seat': max(option_premiums.get('has_heated_seat', 0), 15),
    'has_led_lamp': max(option_premiums.get('has_led_lamp', 0), 20),
    'has_navigation': max(option_premiums.get('has_navigation', 0), 10),
    'has_smart_key': max(option_premiums.get('has_smart_key', 0), 10),
    'has_rear_camera': max(option_premiums.get('has_rear_camera', 0), 5),
}
print("\n✅ 최종 옵션 프리미엄 테이블:")
for opt, p in OPTION_PREMIUM.items():
    print(f"   {opt}: +{p:.0f}만원")

# ========== 기본가격 피처 (옵션 제외) ==========
df['MSRP'] = df['Model'].apply(lambda x: get_msrp(x, False))

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

df['Model_enc'] = df['Model'].map(model_enc).fillna(df['Price'].mean())
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])

# 옵션 프리미엄 계산
df['Option_Premium_Value'] = sum(df[c] * OPTION_PREMIUM[c] for c in opt_cols)

# 기본가격 = 실제가격 - 옵션프리미엄 (학습용)
df['Base_Price'] = df['Price'] - df['Option_Premium_Value']
df['Base_Price'] = df['Base_Price'].clip(lower=50)  # 최소 50만원

print(f"\n✓ 기본가격 계산 완료")
print(f"   평균 옵션 프리미엄: {df['Option_Premium_Value'].mean():.0f}만원")

# ========== 기본가격 모델 학습 ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

features = [
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc',
    'MSRP', 'Segment',
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
]
# 단조제약: MSRP↑가격↑, Segment↑가격↑, Age↑가격↓, Mileage↑가격↓
mono = (0,0,0, 1,1, -1,-1,-1,-1,-1)

X_train = train_df[features]
y_train = np.log1p(train_df['Base_Price'])  # 기본가격 예측!
X_test = test_df[features]
y_test_base = np.log1p(test_df['Base_Price'])

print(f"\n🔥 기본가격 모델 학습...")
base_model = xgb.XGBRegressor(
    n_estimators=500, max_depth=7, learning_rate=0.05,
    monotone_constraints=mono, early_stopping_rounds=30,
    random_state=42, verbosity=0
)
base_model.fit(X_train, y_train, eval_set=[(X_test, y_test_base)], verbose=False)

# ========== 평가 ==========
print("\n" + "="*70)
print("📈 평가")
print("="*70)

# 기본가격 예측
pred_base = np.expm1(base_model.predict(X_test))
# 최종가격 = 기본가격 + 옵션프리미엄
pred_final = pred_base + test_df['Option_Premium_Value'].values
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

# ========== 저장 ==========
joblib.dump(base_model, 'models/domestic_v6.pkl')
joblib.dump(features, 'models/domestic_v6_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
    'option_premium': OPTION_PREMIUM,
}, 'models/domestic_v6_encoders.pkl')

# ========== 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v6(name, year, mileage, opts=None):
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
    }
    
    base_price = np.expm1(base_model.predict(pd.DataFrame([f])[features])[0])
    
    # 옵션 프리미엄 추가
    opt_premium = 0
    if opts:
        for opt, val in opts.items():
            if val and opt in OPTION_PREMIUM:
                opt_premium += OPTION_PREMIUM[opt]
    
    return base_price + opt_premium, base_price, opt_premium

print("\n1️⃣ 동일조건 서열 (2022년 3만km 기본옵션):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    total, base, opt = predict_v6(name, 2022, 30000, {'has_smart_key':1})
    st = "✅" if total >= prev else "⚠️"
    print(f"   {name:20}: {total:,.0f}만원 (기본:{base:,.0f} + 옵션:{opt:,.0f}) {st}")
    prev = total

print("\n2️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_total, no_base, no_opt = predict_v6('더 뉴 그랜저 IG', 2022, 30000, {})
full_total, full_base, full_opt = predict_v6('더 뉴 그랜저 IG', 2022, 30000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
diff = full_total - no_total
print(f"   노옵션: {no_total:,.0f}만원 (기본:{no_base:,.0f} + 옵션:{no_opt:,.0f})")
print(f"   풀옵션: {full_total:,.0f}만원 (기본:{full_base:,.0f} + 옵션:{full_opt:,.0f})")
print(f"   차이: +{diff:,.0f}만원 {'✅정상!' if diff>100 else '⚠️'}")

print("\n3️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av, _, _ = predict_v6('아반떼 (CN7)', 2024, 10000, 
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so, _, _ = predict_v6('쏘나타 (DN8)', 2018, 100000, {})
print(f"   아반떼 2024년 1만km 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈 (정상)' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n4️⃣ 옵션별 프리미엄:")
print("-"*60)
base, _, _ = predict_v6('더 뉴 그랜저 IG', 2022, 30000, {})
for opt in ['has_sunroof','has_leather_seat','has_ventilated_seat','has_led_lamp','has_smart_key']:
    with_opt, _, _ = predict_v6('더 뉴 그랜저 IG', 2022, 30000, {opt: 1})
    print(f"   {opt:20}: +{with_opt-base:,.0f}만원")

print("\n" + "="*70)
print("✅ V6 완료! 옵션 프리미엄 분리 적용")
print("="*70)
