"""
V8 Production: 트림 분리 + 스무딩 + 2단계 모델
==============================================
1. 트림(Trim) 추출 및 분리
2. Target Encoding 스무딩 적용
3. 2단계 모델 (기본가격 → 잔차 보정)
목표: MAPE ≤ 10%, 서열 역전 0%, 옵션 효과 정상
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
print("🚗 V8 Production: 트림 분리 + 스무딩 + 2단계 모델")
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

# ========== 2. 트림 추출 ==========
print("\n🔧 Step 2: 트림 추출...")

# 트림 키워드 정의 (계층적)
TRIM_KEYWORDS = {
    # 최고급 (5)
    '익스클루시브': 5, '캘리그라피': 5, '르블랑': 5, '그래비티': 5,
    # 고급 (4)
    '인스퍼레이션': 4, '프리미엄 플러스': 4, '시그니처': 4, '노블레스': 4,
    'X Line': 4, '프레스티지': 4, '센세이션': 4,
    # 중상급 (3)
    '프리미엄': 3, '프리미어': 3, '럭셔리': 3, '스포츠': 3, '모던 스페셜': 3,
    # 중급 (2)
    '모던': 2, '트렌디': 2, '스타일': 2, '디럭스': 2,
    # 기본 (1)
    '스마트': 1, '밸류': 1, '베이직': 1, 'GLS': 1, 'VXL': 1, 'GXL': 1,
}

def extract_trim(region_text):
    """region 컬럼에서 트림 정보 추출 - 개선된 버전"""
    if pd.isna(region_text) or '주소' in str(region_text):
        return 'unknown', 2
    
    text = str(region_text)
    
    # 패턴: "모델명   배기량 트림 지역" 에서 트림 추출
    # 더 긴 키워드부터 매칭 (프리미엄 플러스 > 프리미엄)
    best_trim = None
    best_rank = 0
    
    for trim, rank in sorted(TRIM_KEYWORDS.items(), key=lambda x: (-len(x[0]), -x[1])):
        if trim in text:
            if rank > best_rank:  # 더 높은 등급 우선
                best_trim = trim
                best_rank = rank
    
    if best_trim:
        return best_trim, best_rank
    
    # 숫자 배기량 다음의 단어를 트림으로 추정
    import re
    match = re.search(r'\d\.\d\s+([가-힣A-Za-z]+)', text)
    if match:
        return match.group(1), 2
    
    return 'standard', 2

df['Trim'], df['Trim_Rank'] = zip(*df['region'].apply(extract_trim))

# 트림 분포 확인
trim_counts = df['Trim'].value_counts()
print(f"✓ 트림 분포 (상위 10개):")
for trim, cnt in trim_counts.head(10).items():
    print(f"   {trim}: {cnt:,}개 ({cnt/len(df)*100:.1f}%)")

# Model + Trim 조합
df['Model_Trim'] = df['Model'] + '_' + df['Trim']
print(f"✓ 모델+트림 조합: {df['Model_Trim'].nunique()}개")

# ========== 3. Target Encoding with Smoothing ==========
print("\n⚙️ Step 3: Target Encoding with Smoothing...")

def smooth_target_encoding(df, group_col, target_col, min_samples=30):
    """스무딩이 적용된 Target Encoding"""
    global_mean = df[target_col].mean()
    group_stats = df.groupby(group_col)[target_col].agg(['mean', 'count'])
    
    # 스무딩: n이 작을수록 전체 평균에 가깝게
    smoothed = (group_stats['mean'] * group_stats['count'] + global_mean * min_samples) / (group_stats['count'] + min_samples)
    
    return smoothed.to_dict(), global_mean

# 주행거리 구간
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)

# 조합 키 생성
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']
df['Model_Trim_Year'] = df['Model_Trim'] + '_' + df['YearOnly'].astype(str)

# 스무딩 적용 인코딩
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

print(f"✓ 스무딩 적용 완료 (min_samples=20~50)")

# ========== 4. 추가 피처 ==========
print("\n📊 Step 4: 추가 피처...")

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])

# 무사고, 검사등급
df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

# 옵션
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0) if c in df.columns else 0
df['Opt_Count'] = sum(df[c] for c in opt_cols)

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
    return 3
df['Segment'] = df['Model'].apply(get_seg)

# ========== 5. Train/Test Split ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 6. 1단계 모델: 기본가격 예측 ==========
print("\n" + "="*70)
print("🔥 1단계 모델: 기본가격 예측")
print("="*70)

stage1_features = [
    'Model_enc', 'Model_Trim_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    'Trim_Rank',  # 트림 등급 추가!
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
    'Segment', 'is_accident_free', 'inspection_grade_enc',
]

# 단조제약
mono_stage1 = (0,0,0,0,0, 1, -1,-1,-1,-1,-1, 1,1,1)

X_train_s1 = train_df[stage1_features]
y_train_s1 = np.log1p(train_df['Price'])
X_test_s1 = test_df[stage1_features]
y_test_s1 = np.log1p(test_df['Price'])

model_stage1 = xgb.XGBRegressor(
    n_estimators=800,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    monotone_constraints=mono_stage1,
    early_stopping_rounds=50,
    random_state=42,
    verbosity=0
)
model_stage1.fit(X_train_s1, y_train_s1, eval_set=[(X_test_s1, y_test_s1)], verbose=False)

# 1단계 예측
train_pred_s1 = model_stage1.predict(X_train_s1)
test_pred_s1 = model_stage1.predict(X_test_s1)

# 1단계 평가
pred_s1 = np.expm1(test_pred_s1)
actual = test_df['Price'].values
mape_s1 = np.mean(np.abs(actual - pred_s1) / actual) * 100
print(f"✓ 1단계 MAPE: {mape_s1:.1f}%")

# ========== 7. 2단계 모델: 잔차 보정 ==========
print("\n" + "="*70)
print("🔥 2단계 모델: 잔차(옵션/디테일) 보정")
print("="*70)

# 잔차 계산
train_df['Residual'] = y_train_s1 - train_pred_s1
test_df['Residual'] = y_test_s1 - test_pred_s1

stage2_features = [
    # 1단계 예측값
    'Stage1_Pred',
    # 옵션 피처 (여기서 학습!)
    'Opt_Count', 'has_sunroof', 'has_leather_seat', 'has_led_lamp', 
    'has_smart_key', 'has_ventilated_seat', 'has_heated_seat',
    # 트림
    'Trim_Rank',
]

train_df['Stage1_Pred'] = train_pred_s1
test_df['Stage1_Pred'] = test_pred_s1

# 단조제약: 옵션은 증가
mono_stage2 = (0, 1,1,1,1,1,1,1, 1)

X_train_s2 = train_df[stage2_features]
y_train_s2 = train_df['Residual']
X_test_s2 = test_df[stage2_features]

model_stage2 = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.03,
    subsample=0.8,
    monotone_constraints=mono_stage2,
    early_stopping_rounds=30,
    random_state=42,
    verbosity=0
)
model_stage2.fit(X_train_s2, y_train_s2, eval_set=[(X_test_s2, test_df['Residual'])], verbose=False)

# 2단계 보정
test_pred_s2 = model_stage2.predict(X_test_s2)

# ========== 8. 최종 예측 ==========
print("\n" + "="*70)
print("📈 최종 평가")
print("="*70)

final_pred_log = test_pred_s1 + test_pred_s2
final_pred = np.expm1(final_pred_log)

mae = mean_absolute_error(actual, final_pred)
mape = np.mean(np.abs(actual - final_pred) / actual) * 100
r2 = r2_score(y_test_s1, final_pred_log)

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}% (목표: ≤10%)")

errors = np.abs(actual - final_pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

# Feature Importance
print("\n⭐ 1단계 Feature Importance:")
for f,i in sorted(zip(stage1_features, model_stage1.feature_importances_), key=lambda x:-x[1])[:8]:
    print(f"   {f}: {i:.4f}")

print("\n⭐ 2단계 Feature Importance:")
for f,i in sorted(zip(stage2_features, model_stage2.feature_importances_), key=lambda x:-x[1])[:8]:
    print(f"   {f}: {i:.4f}")

# ========== 9. 저장 ==========
print("\n💾 저장...")
joblib.dump({
    'stage1': model_stage1, 
    'stage2': model_stage2
}, 'models/domestic_v8.pkl')
joblib.dump({
    'stage1': stage1_features, 
    'stage2': stage2_features
}, 'models/domestic_v8_features.pkl')
joblib.dump({
    'model_enc': model_enc,
    'model_trim_enc': model_trim_enc,
    'model_year_enc': model_year_enc,
    'model_year_mg_enc': model_year_mg_enc,
    'brand_enc': brand_enc,
    'global_mean': global_mean,
}, 'models/domestic_v8_encoders.pkl')
print("✅ 저장 완료!")

# ========== 10. 핵심 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v8(name, year, mileage, trim='standard', opts=None, accident_free=1, grade='normal'):
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
        'Age': age, 'Age_log': np.log1p(age),
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'Segment': get_seg(name),
        'is_accident_free': accident_free,
        'inspection_grade_enc': grade_enc,
    }
    
    pred_s1 = model_stage1.predict(pd.DataFrame([f_s1])[stage1_features])[0]
    
    # 2단계 피처
    opt_count = sum(opts.values()) if opts else 0
    f_s2 = {
        'Stage1_Pred': pred_s1,
        'Opt_Count': opt_count,
        'has_sunroof': opts.get('has_sunroof', 0) if opts else 0,
        'has_leather_seat': opts.get('has_leather_seat', 0) if opts else 0,
        'has_led_lamp': opts.get('has_led_lamp', 0) if opts else 0,
        'has_smart_key': opts.get('has_smart_key', 0) if opts else 0,
        'has_ventilated_seat': opts.get('has_ventilated_seat', 0) if opts else 0,
        'has_heated_seat': opts.get('has_heated_seat', 0) if opts else 0,
        'Trim_Rank': trim_rank,
    }
    
    pred_s2 = model_stage2.predict(pd.DataFrame([f_s2])[stage2_features])[0]
    
    return np.expm1(pred_s1 + pred_s2), np.expm1(pred_s1), pred_s2

print("\n1️⃣ 동일조건 서열 (2022년 3만km, 기본트림):")
print("-"*60)
prev = 0
for name in ['모닝','아반떼 (CN7)','쏘나타 (DN8)','더 뉴 그랜저 IG','G70','G80 (RG3)','G90']:
    p, base, adj = predict_v8(name, 2022, 30000, 'standard', {'has_smart_key':1})
    st = "✅" if p >= prev else "⚠️"
    print(f"   {name:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n2️⃣ 트림별 가격 (쏘나타 2022년 3만km):")
print("-"*60)
for trim, rank in [('스마트', 1), ('모던', 2), ('프리미엄', 3), ('인스퍼레이션', 4)]:
    p, _, _ = predict_v8('쏘나타 (DN8)', 2022, 30000, trim, {'has_smart_key':1})
    print(f"   {trim:15}: {p:,.0f}만원 (등급:{rank})")

print("\n3️⃣ 옵션 효과 (그랜저 2022년 3만km):")
print("-"*60)
no_opt, b1, _ = predict_v8('더 뉴 그랜저 IG', 2022, 30000, 'standard', {})
full_opt, b2, _ = predict_v8('더 뉴 그랜저 IG', 2022, 30000, 'standard',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1})
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: +{full_opt-no_opt:,.0f}만원 {'✅' if full_opt>no_opt else '❌'}")

print("\n4️⃣ 아반떼 최신풀옵 vs 소나타 구형노옵:")
print("-"*60)
av, _, _ = predict_v8('아반떼 (CN7)', 2024, 10000, '인스퍼레이션',
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1})
so, _, _ = predict_v8('쏘나타 (DN8)', 2018, 100000, '스마트', {})
print(f"   아반떼 2024년 1만km 인스퍼레이션 풀옵: {av:,.0f}만원")
print(f"   소나타 2018년 10만km 스마트 노옵: {so:,.0f}만원")
print(f"   → {'✅ 아반떼가 비쌈' if av>so else '⚠️ 소나타가 비쌈'}")

print("\n" + "="*70)
print("✅ V8 Production 완료!")
print("="*70)
