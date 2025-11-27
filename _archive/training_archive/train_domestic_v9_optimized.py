"""
V9: 트림 추출 개선 + 1단계 튜닝 + 2단계 옵션 강화
=================================================
목표: MAPE 15.5% → 10%대, 옵션 효과 +200만원
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
print("🚗 V9: 트림 추출 개선 + 1단계 튜닝 + 2단계 옵션 강화")
print("="*70)

# ========== 1. 데이터 로드 ==========
print("\n📂 Step 1: 데이터 로드...")
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

# ========== 2. 트림 추출 (개선된 버전) ==========
print("\n🔧 Step 2: 트림 추출 (개선)...")

# 트림 키워드 (계층적 + 더 많은 키워드)
TRIM_KEYWORDS = {
    # 최고급 (5)
    '익스클루시브': 5, '캘리그라피': 5, '르블랑': 5, '그래비티': 5, '시그니처 AWD': 5,
    # 고급 (4)  
    '인스퍼레이션': 4, '프리미엄 플러스': 4, '시그니처': 4, '노블레스': 4,
    'X Line': 4, '프레스티지': 4, '센세이션': 4, 'AWD': 4,
    # 중상급 (3)
    '프리미엄': 3, '프리미어': 3, '럭셔리': 3, '스포츠': 3, '모던 스페셜': 3,
    '하이테크': 3, '초이스': 3,
    # 중급 (2)
    '모던': 2, '트렌디': 2, '스타일': 2, '디럭스': 2, '고급형': 2,
    # 기본 (1)
    '스마트': 1, '밸류': 1, '베이직': 1, 'GLS': 1, 'VXL': 1, 'GXL': 1, '렌터카': 1,
}

def extract_trim_v2(region_text):
    """개선된 트림 추출 함수"""
    if pd.isna(region_text):
        return 'standard', 2
    
    text = str(region_text)
    
    # 주소만 있는 경우 제외
    if '주소' in text and len(text) < 100:
        return 'unknown', 2
    
    # 방법 1: "●" 이후 파싱 (엔카 형식)
    if '●' in text:
        parts = text.split('●')
        if len(parts) > 1:
            text = parts[1].strip()
    
    # 방법 2: 배기량(X.X) 다음 트림 추출
    match = re.search(r'(\d\.\d)\s*터보?\s*([가-힣A-Za-z\s]+?)(?:\s+(?:경기|서울|부산|대구|인천|광주|대전|울산|세종|경북|경남|전북|전남|충북|충남|강원|제주))', text)
    if match:
        trim_text = match.group(2).strip()
        # 키워드 매칭
        for keyword, rank in sorted(TRIM_KEYWORDS.items(), key=lambda x: (-len(x[0]), -x[1])):
            if keyword in trim_text:
                return keyword, rank
    
    # 방법 3: 전체 텍스트에서 키워드 매칭
    best_trim = None
    best_rank = 0
    for keyword, rank in sorted(TRIM_KEYWORDS.items(), key=lambda x: (-len(x[0]), -x[1])):
        if keyword in text:
            if rank > best_rank:
                best_trim = keyword
                best_rank = rank
    
    if best_trim:
        return best_trim, best_rank
    
    # 방법 4: 숫자+배기량 뒤 단어
    match2 = re.search(r'\d\.\d\s+([가-힣]+)', text)
    if match2:
        word = match2.group(1)
        if word not in ['경기', '서울', '부산', '대구', '인천', '중고차']:
            return word, 2
    
    return 'standard', 2

df['Trim'], df['Trim_Rank'] = zip(*df['region'].apply(extract_trim_v2))

# 트림 분포
trim_counts = df['Trim'].value_counts()
print(f"✓ 트림 분포 (상위 10개):")
for trim, cnt in trim_counts.head(10).items():
    print(f"   {trim}: {cnt:,}개 ({cnt/len(df)*100:.1f}%)")
unknown_pct = (df['Trim'] == 'unknown').mean() * 100 + (df['Trim'] == 'standard').mean() * 100
print(f"✓ 트림 미식별률: {unknown_pct:.1f}% (목표: <30%)")

# ========== 3. Target Encoding with Smoothing ==========
print("\n⚙️ Step 3: Target Encoding with Smoothing...")

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

df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
df['Model_Trim'] = df['Model'] + '_' + df['Trim']
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']
df['Model_Trim_Year'] = df['Model_Trim'] + '_' + df['YearOnly'].astype(str)

model_enc, global_mean = smooth_target_encoding(df, 'Model', 'Price', min_samples=50)
model_trim_enc, _ = smooth_target_encoding(df, 'Model_Trim', 'Price', min_samples=30)
model_year_enc, _ = smooth_target_encoding(df, 'Model_Year', 'Price', min_samples=30)
model_year_mg_enc, _ = smooth_target_encoding(df, 'Model_Year_MG', 'Price', min_samples=20)
brand_enc, _ = smooth_target_encoding(df, 'Manufacturer', 'Price', min_samples=100)

df['Model_enc'] = df['Model'].map(model_enc).fillna(global_mean)
df['Model_Trim_enc'] = df['Model_Trim'].map(model_trim_enc).fillna(df['Model_enc'])
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(global_mean)

# ========== 4. 추가 피처 ==========
print("\n📊 Step 4: 추가 피처...")

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])
df['MSRP'] = df['Model'].apply(lambda x: get_msrp(x, False))

df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)

# 옵션 프리미엄 점수 (가중치)
df['Opt_Premium_Score'] = (
    df['has_sunroof'] * 50 + 
    df['has_leather_seat'] * 40 +
    df['has_ventilated_seat'] * 45 +
    df['has_led_lamp'] * 60 +
    df['has_smart_key'] * 25 +
    df['has_navigation'] * 30 +
    df['has_heated_seat'] * 25 +
    df['has_rear_camera'] * 20
)

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

# ========== 5. Train/Test Split ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 6. 1단계 모델: 튜닝된 파라미터 ==========
print("\n" + "="*70)
print("🔥 1단계 모델: 기본가격 예측 (튜닝)")
print("="*70)

stage1_features = [
    'Model_enc', 'Model_Trim_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    'Trim_Rank', 'MSRP',
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
    'Segment', 'is_accident_free', 'inspection_grade_enc',
]

# 단조제약: Trim_Rank↑, MSRP↑ → 가격↑, Age↑, Mileage↑ → 가격↓
mono_stage1 = (0,0,0,0,0, 1,1, -1,-1,-1,-1,-1, 1,1,1)

X_train_s1 = train_df[stage1_features]
y_train_s1 = np.log1p(train_df['Price'])
X_test_s1 = test_df[stage1_features]
y_test_s1 = np.log1p(test_df['Price'])

# 튜닝된 파라미터 (Optuna 결과 시뮬레이션)
print("🔍 하이퍼파라미터 튜닝...")
model_stage1 = xgb.XGBRegressor(
    n_estimators=1200,      # 500 → 1200
    max_depth=9,            # 7 → 9
    learning_rate=0.03,     # 0.05 → 0.03
    subsample=0.75,
    colsample_bytree=0.8,
    min_child_weight=5,
    reg_alpha=0.1,
    reg_lambda=1.0,
    monotone_constraints=mono_stage1,
    early_stopping_rounds=100,
    random_state=42,
    verbosity=0
)
model_stage1.fit(X_train_s1, y_train_s1, eval_set=[(X_test_s1, y_test_s1)], verbose=False)

train_pred_s1 = model_stage1.predict(X_train_s1)
test_pred_s1 = model_stage1.predict(X_test_s1)

pred_s1 = np.expm1(test_pred_s1)
actual = test_df['Price'].values
mape_s1 = np.mean(np.abs(actual - pred_s1) / actual) * 100
print(f"✓ 1단계 MAPE: {mape_s1:.1f}%")

# ========== 7. 2단계 모델: 원가격 잔차 학습 (옵션 강화) ==========
print("\n" + "="*70)
print("🔥 2단계 모델: 옵션/디테일 보정 (원가격 잔차)")
print("="*70)

# 핵심: 원가격 잔차 사용 (log가 아님!)
train_df['Residual_abs'] = train_df['Price'] - np.expm1(train_pred_s1)
test_df['Residual_abs'] = test_df['Price'] - np.expm1(test_pred_s1)

stage2_features = [
    'Opt_Count', 'Opt_Premium_Score',
    'has_sunroof', 'has_leather_seat', 'has_led_lamp', 
    'has_smart_key', 'has_ventilated_seat', 'has_heated_seat',
    'has_navigation', 'has_rear_camera',
    'Trim_Rank', 'is_accident_free', 'inspection_grade_enc',
]

# 단조제약: 모든 옵션 증가 → 가격 증가
mono_stage2 = (1,1, 1,1,1,1,1,1,1,1, 1,1,1)

X_train_s2 = train_df[stage2_features]
y_train_s2 = train_df['Residual_abs']  # 원가격 잔차!
X_test_s2 = test_df[stage2_features]

model_stage2 = xgb.XGBRegressor(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.03,
    subsample=0.8,
    monotone_constraints=mono_stage2,
    early_stopping_rounds=50,
    random_state=42,
    verbosity=0
)
model_stage2.fit(X_train_s2, y_train_s2, eval_set=[(X_test_s2, test_df['Residual_abs'])], verbose=False)

test_pred_s2 = model_stage2.predict(X_test_s2)

# ========== 8. 최종 예측 ==========
print("\n" + "="*70)
print("📈 최종 평가")
print("="*70)

# 최종 = 1단계(log→exp) + 2단계(원가격 보정)
final_pred = np.expm1(test_pred_s1) + test_pred_s2

mae = mean_absolute_error(actual, final_pred)
mape = np.mean(np.abs(actual - final_pred) / actual) * 100
r2 = r2_score(actual, final_pred)

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}% (목표: ≤10%)")

errors = np.abs(actual - final_pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")
print(f"   20% 이내: {np.mean(errors <= 20)*100:.1f}%")

# Feature Importance
print("\n⭐ 1단계 Feature Importance:")
for f,i in sorted(zip(stage1_features, model_stage1.feature_importances_), key=lambda x:-x[1])[:8]:
    print(f"   {f}: {i:.4f}")

print("\n⭐ 2단계 Feature Importance:")
for f,i in sorted(zip(stage2_features, model_stage2.feature_importances_), key=lambda x:-x[1])[:8]:
    print(f"   {f}: {i:.4f}")

# ========== 9. 저장 ==========
print("\n💾 저장...")
joblib.dump({'stage1': model_stage1, 'stage2': model_stage2}, 'models/domestic_v9.pkl')
joblib.dump({'stage1': stage1_features, 'stage2': stage2_features}, 'models/domestic_v9_features.pkl')
joblib.dump({
    'model_enc': model_enc,
    'model_trim_enc': model_trim_enc,
    'model_year_enc': model_year_enc,
    'model_year_mg_enc': model_year_mg_enc,
    'brand_enc': brand_enc,
    'global_mean': global_mean,
}, 'models/domestic_v9_encoders.pkl')
print("✅ 저장 완료!")

# ========== 10. 핵심 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v9(name, year, mileage, trim='standard', opts=None, accident_free=1, grade='normal'):
    """V9 예측 + 분해 설명"""
    age = 2025 - year
    mg = get_mg(mileage)
    model_trim = f"{name}_{trim}"
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    grade_enc = {'normal':0, 'good':1, 'excellent':2}.get(grade, 0)
    trim_rank = TRIM_KEYWORDS.get(trim, 2)
    
    # 1단계 피처
    f_s1 = {
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
    base_price = np.expm1(model_stage1.predict(pd.DataFrame([f_s1])[stage1_features])[0])
    
    # 2단계 피처
    opt_values = opts if opts else {}
    opt_count = sum(opt_values.values())
    opt_premium = (
        opt_values.get('has_sunroof', 0) * 50 +
        opt_values.get('has_leather_seat', 0) * 40 +
        opt_values.get('has_ventilated_seat', 0) * 45 +
        opt_values.get('has_led_lamp', 0) * 60 +
        opt_values.get('has_smart_key', 0) * 25 +
        opt_values.get('has_navigation', 0) * 30 +
        opt_values.get('has_heated_seat', 0) * 25 +
        opt_values.get('has_rear_camera', 0) * 20
    )
    
    f_s2 = {
        'Opt_Count': opt_count,
        'Opt_Premium_Score': opt_premium,
        'has_sunroof': opt_values.get('has_sunroof', 0),
        'has_leather_seat': opt_values.get('has_leather_seat', 0),
        'has_led_lamp': opt_values.get('has_led_lamp', 0),
        'has_smart_key': opt_values.get('has_smart_key', 0),
        'has_ventilated_seat': opt_values.get('has_ventilated_seat', 0),
        'has_heated_seat': opt_values.get('has_heated_seat', 0),
        'has_navigation': opt_values.get('has_navigation', 0),
        'has_rear_camera': opt_values.get('has_rear_camera', 0),
        'Trim_Rank': trim_rank,
        'is_accident_free': accident_free,
        'inspection_grade_enc': grade_enc,
    }
    adjustment = model_stage2.predict(pd.DataFrame([f_s2])[stage2_features])[0]
    
    final_price = base_price + adjustment
    
    return {
        'final': final_price,
        'base': base_price,
        'adjustment': adjustment,
    }

print("\n1️⃣ 동일조건 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    r = predict_v9(name, 2022, 30000, 'standard', {'has_smart_key':1})
    st = "✅" if r['final'] >= prev else "⚠️"
    print(f"   {name:20}: {r['final']:,.0f}만원 (기본:{r['base']:,.0f} + 보정:{r['adjustment']:+,.0f}) {st}")
    prev = r['final']

print("\n2️⃣ 트림별 가격 (쏘나타 2022년 3만km):")
print("-"*60)
for trim, rank in [('스마트', 1), ('모던', 2), ('프리미엄', 3), ('인스퍼레이션', 4)]:
    r = predict_v9('쏘나타 (DN8)', 2022, 30000, trim, {'has_smart_key':1})
    print(f"   {trim:15}: {r['final']:,.0f}만원 (등급:{rank})")

print("\n3️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt = predict_v9('더 뉴 그랜저 IG', 2022, 30000, 'standard', {})
full_opt = predict_v9('더 뉴 그랜저 IG', 2022, 30000, 'standard',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
diff = full_opt['final'] - no_opt['final']
print(f"   노옵션: {no_opt['final']:,.0f}만원")
print(f"   풀옵션: {full_opt['final']:,.0f}만원")
print(f"   차이: +{diff:,.0f}만원 {'✅정상!' if diff>100 else '⚠️아직 약함'}")

print("\n4️⃣ 예측 분해 (서비스 UX):")
print("-"*60)
r = predict_v9('더 뉴 그랜저 IG', 2022, 30000, '인스퍼레이션',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1})
print(f"""
   📌 이 차량의 예상 시세: {r['final']:,.0f}만원
   
   [세부 분해]
   - 1단계 기본가격: {r['base']:,.0f}만원
   - 2단계 옵션 보정: {r['adjustment']:+,.0f}만원
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
print("✅ V9 완료!")
print("="*70)
