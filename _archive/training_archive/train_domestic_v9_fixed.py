"""
V9 Fixed: 1단계 튜닝 + 옵션 프리미엄 고정 테이블
===============================================
- 1단계: 튜닝된 XGBoost (기본가격)
- 2단계: 옵션 프리미엄 고정 테이블 (데이터 기반)
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
from msrp_data import get_msrp

print("="*70)
print("🚗 V9 Fixed: 1단계 튜닝 + 옵션 프리미엄 고정")
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
print(f"✓ 데이터: {len(df):,}행")

# ========== 2. 트림 추출 ==========
TRIM_KEYWORDS = {
    '익스클루시브': 5, '캘리그라피': 5, '르블랑': 5, '그래비티': 5,
    '인스퍼레이션': 4, '프리미엄 플러스': 4, '시그니처': 4, '노블레스': 4,
    '프레스티지': 4, 'AWD': 4,
    '프리미엄': 3, '프리미어': 3, '럭셔리': 3, '스포츠': 3,
    '모던': 2, '트렌디': 2, '스타일': 2, '디럭스': 2,
    '스마트': 1, '밸류': 1, '베이직': 1,
}

def extract_trim(region_text):
    if pd.isna(region_text) or '주소' in str(region_text):
        return 'unknown', 2
    text = str(region_text)
    for trim, rank in sorted(TRIM_KEYWORDS.items(), key=lambda x: (-len(x[0]), -x[1])):
        if trim in text:
            return trim, rank
    return 'standard', 2

df['Trim'], df['Trim_Rank'] = zip(*df['region'].apply(extract_trim))

# ========== 3. 옵션 프리미엄 분석 (데이터 기반) ==========
print("\n📊 옵션 프리미엄 분석...")
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0

# 동일 Model_Year 그룹 내에서 옵션 있는 차 vs 없는 차 가격 차이
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
option_premiums = {}
for opt in opt_cols:
    with_opt = df[df[opt] == 1].groupby('Model_Year')['Price'].mean()
    without_opt = df[df[opt] == 0].groupby('Model_Year')['Price'].mean()
    common = with_opt.index.intersection(without_opt.index)
    if len(common) > 50:
        diff = (with_opt[common] - without_opt[common]).median()
        option_premiums[opt] = max(30, diff)  # 최소 30만원
    else:
        option_premiums[opt] = 50  # 기본값

print("✓ 옵션 프리미엄 (데이터 기반):")
for opt, p in sorted(option_premiums.items(), key=lambda x: -x[1]):
    print(f"   {opt}: +{p:.0f}만원")

# 옵션 프리미엄 계산
df['Option_Premium'] = sum(df[c] * option_premiums[c] for c in opt_cols)

# 기본가격 = 전체가격 - 옵션프리미엄
df['Base_Price'] = (df['Price'] - df['Option_Premium']).clip(lower=50)

# ========== 4. Target Encoding ==========
def smooth_target_encoding(df, group_col, target_col, min_samples=30):
    global_mean = df[target_col].mean()
    group_stats = df.groupby(group_col)[target_col].agg(['mean', 'count'])
    smoothed = (group_stats['mean'] * group_stats['count'] + global_mean * min_samples) / (group_stats['count'] + min_samples)
    return smoothed.to_dict(), global_mean

def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)

df['Model_Trim'] = df['Model'] + '_' + df['Trim']
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']

# 기본가격 기준 인코딩
model_enc, global_mean = smooth_target_encoding(df, 'Model', 'Base_Price', min_samples=50)
model_trim_enc, _ = smooth_target_encoding(df, 'Model_Trim', 'Base_Price', min_samples=30)
model_year_enc, _ = smooth_target_encoding(df, 'Model_Year', 'Base_Price', min_samples=30)
model_year_mg_enc, _ = smooth_target_encoding(df, 'Model_Year_MG', 'Base_Price', min_samples=20)
brand_enc, _ = smooth_target_encoding(df, 'Manufacturer', 'Base_Price', min_samples=100)

df['Model_enc'] = df['Model'].map(model_enc).fillna(global_mean)
df['Model_Trim_enc'] = df['Model_Trim'].map(model_trim_enc).fillna(df['Model_enc'])
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(global_mean)

# ========== 5. 추가 피처 ==========
df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])
df['MSRP'] = df['Model'].apply(lambda x: get_msrp(x, False))

df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

def get_seg(m):
    m = str(m).lower()
    if any(x in m for x in ['모닝','스파크','레이']): return 1
    if any(x in m for x in ['아반떼','k3']): return 2
    if any(x in m for x in ['쏘나타','k5']): return 3
    if any(x in m for x in ['그랜저','k7','k8']): return 4
    if any(x in m for x in ['k9','g70']): return 5
    if any(x in m for x in ['g80','gv80']): return 6
    if any(x in m for x in ['g90']): return 7
    return 3
df['Segment'] = df['Model'].apply(get_seg)

# ========== 6. Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# ========== 7. 1단계 모델 (기본가격 예측) ==========
print("\n🔥 1단계: 기본가격 예측...")

features = [
    'Model_enc', 'Model_Trim_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    'Trim_Rank', 'MSRP',
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
    'Segment', 'is_accident_free', 'inspection_grade_enc',
]

mono = (0,0,0,0,0, 1,1, -1,-1,-1,-1,-1, 1,1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Base_Price'])
X_test = test_df[features]

model = xgb.XGBRegressor(
    n_estimators=1000,
    max_depth=8,
    learning_rate=0.04,
    subsample=0.8,
    colsample_bytree=0.8,
    monotone_constraints=mono,
    early_stopping_rounds=50,
    random_state=42,
    verbosity=0
)
model.fit(X_train, y_train, eval_set=[(X_test, np.log1p(test_df['Base_Price']))], verbose=False)

# ========== 8. 평가 ==========
print("\n" + "="*70)
print("📈 평가")
print("="*70)

# 기본가격 예측
pred_base = np.expm1(model.predict(X_test))
# 최종가격 = 기본가격 + 옵션프리미엄
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

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:10]:
    print(f"   {f}: {i:.4f}")

# ========== 9. 저장 ==========
joblib.dump(model, 'models/domestic_v9_fixed.pkl')
joblib.dump(features, 'models/domestic_v9_fixed_features.pkl')
joblib.dump({
    'model_enc': model_enc,
    'model_trim_enc': model_trim_enc,
    'model_year_enc': model_year_enc,
    'model_year_mg_enc': model_year_mg_enc,
    'brand_enc': brand_enc,
    'global_mean': global_mean,
    'option_premiums': option_premiums,
}, 'models/domestic_v9_fixed_encoders.pkl')
print("✅ 저장 완료!")

# ========== 10. 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v9(name, year, mileage, trim='standard', opts=None, accident_free=1, grade='normal'):
    age = 2025 - year
    mg = get_mg(mileage)
    model_trim = f"{name}_{trim}"
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    grade_enc = {'normal':0, 'good':1, 'excellent':2}.get(grade, 0)
    trim_rank = TRIM_KEYWORDS.get(trim, 2)
    
    f = {
        'Model_enc': model_enc.get(name, global_mean),
        'Model_Trim_enc': model_trim_enc.get(model_trim, model_enc.get(name, global_mean)),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, global_mean)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, global_mean)),
        'Brand_enc': 2500,
        'Trim_Rank': trim_rank,
        'MSRP': get_msrp(name, False),
        'Age': age, 'Age_log': np.log1p(age),
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'Segment': get_seg(name),
        'is_accident_free': accident_free,
        'inspection_grade_enc': grade_enc,
    }
    
    base_price = np.expm1(model.predict(pd.DataFrame([f])[features])[0])
    
    opt_premium = 0
    if opts:
        for opt, val in opts.items():
            if val and opt in option_premiums:
                opt_premium += option_premiums[opt]
    
    return {
        'final': base_price + opt_premium,
        'base': base_price,
        'option': opt_premium,
    }

print("\n1️⃣ 동일조건 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    r = predict_v9(name, 2022, 30000, 'standard', {'has_smart_key':1})
    st = "✅" if r['final'] >= prev else "⚠️"
    print(f"   {name:20}: {r['final']:,.0f}만원 {st}")
    prev = r['final']

print("\n2️⃣ 트림별 가격 (쏘나타 2022년 3만km):")
print("-"*60)
prev_p = 0
for trim, rank in [('스마트', 1), ('모던', 2), ('프리미엄', 3), ('인스퍼레이션', 4)]:
    r = predict_v9('쏘나타 (DN8)', 2022, 30000, trim, {'has_smart_key':1})
    st = "✅" if r['final'] >= prev_p else "⚠️"
    print(f"   {trim:15}: {r['final']:,.0f}만원 (등급:{rank}) {st}")
    prev_p = r['final']

print("\n3️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt = predict_v9('더 뉴 그랜저 IG', 2022, 30000, 'standard', {})
full_opt = predict_v9('더 뉴 그랜저 IG', 2022, 30000, 'standard',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
diff = full_opt['final'] - no_opt['final']
print(f"   노옵션: {no_opt['final']:,.0f}만원")
print(f"   풀옵션: {full_opt['final']:,.0f}만원")
print(f"   차이: +{diff:,.0f}만원 {'✅' if diff>200 else '⚠️'}")

print("\n📌 옵션별 프리미엄:")
for opt, p in sorted(option_premiums.items(), key=lambda x: -x[1]):
    print(f"   {opt:20}: +{p:.0f}만원")

print("\n4️⃣ 예측 분해 (서비스 UX):")
print("-"*60)
r = predict_v9('더 뉴 그랜저 IG', 2022, 30000, '인스퍼레이션',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1})
print(f"""
   📌 이 차량의 예상 시세: {r['final']:,.0f}만원
   
   [세부 분해]
   - 기본 차량 가격: {r['base']:,.0f}만원
   - 옵션 프리미엄: +{r['option']:,.0f}만원
     ㄴ 썬루프: +{option_premiums['has_sunroof']:.0f}만원
     ㄴ 가죽시트: +{option_premiums['has_leather_seat']:.0f}만원
     ㄴ LED램프: +{option_premiums['has_led_lamp']:.0f}만원
   ──────────────────────
   - 최종 예측가: {r['final']:,.0f}만원
""")

print("\n5️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av = predict_v9('아반떼 (CN7)', 2024, 10000, '인스퍼레이션',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so = predict_v9('쏘나타 (DN8)', 2018, 100000, '스마트', {})
print(f"   아반떼 2024년 1만km 인스퍼레이션 풀옵: {av['final']:,.0f}만원")
print(f"   소나타 2018년 10만km 스마트 노옵: {so['final']:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈' if av['final']>so['final'] else '⚠️ 소나타가 비쌈'}")

print("\n" + "="*70)
print("✅ V9 Fixed 완료!")
print("="*70)
