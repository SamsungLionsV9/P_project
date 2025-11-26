"""
외제차 V11: 국산차 V11 구조 적용
================================
목표: MAPE ≤12%, 서열 정상, 옵션 효과 정상
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("🚗 외제차 V11: 국산차 V11 구조 적용")
print("="*70)

# ========== 1. 데이터 로드 ==========
df = pd.read_csv('encar_imported_data.csv')
df_detail = pd.read_csv('data/complete_imported_details.csv')
df = df.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df = df[(df['Price'] >= 100) & (df['Price'] <= 100000)]  # 외제차는 더 비쌈
df = df[df['Mileage'] < 300000]
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'])
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['Age'] = 2025 - df['YearOnly']
df['Km_per_Year'] = df['Mileage'] / (df['Age'] + 1)
df = df[df['Km_per_Year'] <= 50000]
print(f"원본 데이터: {len(df):,}행")

# 브랜드 분포
print("\n📊 브랜드 분포:")
for brand, cnt in df['Manufacturer'].value_counts().head(5).items():
    print(f"   {brand}: {cnt:,}개")

# ========== 2. 브랜드 등급 ==========
BRAND_TIER = {
    # 슈퍼카 (6)
    '페라리': 6, '람보르기니': 6, '맥라렌': 6, '롤스로이스': 6, '벤틀리': 6,
    # 하이엔드 (5)
    '포르쉐': 5, '마세라티': 5, 'AMG': 5, 'M': 5,
    # 프리미엄 (4)
    '벤츠': 4, 'BMW': 4, '아우디': 4, '렉서스': 4,
    # 준프리미엄 (3)
    '볼보': 3, '랜드로버': 3, '재규어': 3, '인피니티': 3, '캐딜락': 3, '링컨': 3,
    # 일반 수입 (2)
    '폭스바겐': 2, '미니': 2, '지프': 2, '푸조': 2, '시트로엥': 2, '르노': 2,
    # 전기차 (4)
    '테슬라': 4, '폴스타': 3,
    # 일본차 (3)
    '토요타': 3, '혼다': 3, '닛산': 2,
}
df['Brand_Tier'] = df['Manufacturer'].map(BRAND_TIER).fillna(2)

# ========== 3. 트림(Badge) 파싱 ==========
print("\n🔧 트림(Badge) 파싱...")

# 벤츠/BMW 클래스 추출
def extract_class(model, badge):
    model = str(model).upper()
    badge = str(badge).upper() if pd.notna(badge) else ''
    
    # 벤츠 클래스
    if 'A-CLASS' in model or 'A클래스' in model: return 'A', 1
    if 'B-CLASS' in model or 'B클래스' in model: return 'B', 1
    if 'CLA' in model: return 'CLA', 2
    if 'C-CLASS' in model or 'C클래스' in model: return 'C', 2
    if 'E-CLASS' in model or 'E클래스' in model: return 'E', 3
    if 'S-CLASS' in model or 'S클래스' in model: return 'S', 4
    if 'GLA' in model: return 'GLA', 2
    if 'GLB' in model: return 'GLB', 2
    if 'GLC' in model: return 'GLC', 3
    if 'GLE' in model: return 'GLE', 3
    if 'GLS' in model: return 'GLS', 4
    if 'G-CLASS' in model or 'G클래스' in model: return 'G', 5
    if 'AMG GT' in model: return 'AMG GT', 5
    
    # BMW 시리즈
    if '1시리즈' in model or '1 SERIES' in model: return '1시리즈', 1
    if '2시리즈' in model or '2 SERIES' in model: return '2시리즈', 1
    if '3시리즈' in model or '3 SERIES' in model: return '3시리즈', 2
    if '4시리즈' in model or '4 SERIES' in model: return '4시리즈', 2
    if '5시리즈' in model or '5 SERIES' in model: return '5시리즈', 3
    if '7시리즈' in model or '7 SERIES' in model: return '7시리즈', 4
    if 'X1' in model: return 'X1', 2
    if 'X3' in model: return 'X3', 3
    if 'X5' in model: return 'X5', 4
    if 'X7' in model: return 'X7', 5
    if 'M3' in model: return 'M3', 4
    if 'M5' in model: return 'M5', 5
    
    # 아우디
    if 'A3' in model: return 'A3', 1
    if 'A4' in model: return 'A4', 2
    if 'A6' in model: return 'A6', 3
    if 'A8' in model: return 'A8', 4
    if 'Q3' in model: return 'Q3', 2
    if 'Q5' in model: return 'Q5', 3
    if 'Q7' in model: return 'Q7', 4
    if 'Q8' in model: return 'Q8', 4
    
    return 'Unknown', 2

df['Class'], df['Class_Rank'] = zip(*df.apply(lambda r: extract_class(r['Model'], r['Badge']), axis=1))

print(f"✓ 클래스 분포 (상위 10개):")
for cls, cnt in df['Class'].value_counts().head(10).items():
    print(f"   {cls}: {cnt:,}개")

# ========== 4. 아웃라이어 제거 ==========
print("\n🔍 아웃라이어 제거...")
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
model_year_stats = df.groupby('Model_Year')['Price'].agg(['mean', 'std', 'count'])
df = df.merge(model_year_stats[['mean', 'std']], left_on='Model_Year', right_index=True, suffixes=('', '_my'))
df['z_score'] = np.abs(df['Price'] - df['mean']) / (df['std'] + 1)

print(f"z_score > 2: {(df['z_score'] > 2).sum():,}행")
print(f"z_score > 1.5: {(df['z_score'] > 1.5).sum():,}행")

# 아웃라이어 제거 (국산차보다 약간 느슨하게)
df = df[df['z_score'] <= 1.5].copy()
print(f"정제 후: {len(df):,}행")

# ========== 5. 피처 엔지니어링 ==========
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

# ========== 6. Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"\n✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 7. 피처 ==========
features = [
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc',
    'Brand_Tier', 'Class_Rank',  # 외제차 전용
    'Age', 'Age_log', 'Age_sq',
    'Mileage', 'Mile_log', 'Km_per_Year',
    'is_accident_free', 'inspection_grade_enc',
    'Opt_Count', 'Opt_Premium',
    'has_sunroof', 'has_leather_seat', 'has_led_lamp', 'has_smart_key',
    'has_ventilated_seat', 'has_heated_seat', 'has_navigation', 'has_rear_camera',
]

# 단조제약: 브랜드등급↑, 클래스등급↑, 옵션↑ → 가격↑
mono = (0,0,0,0, 1,1, 0,0,0, 0,0,0, 1,1, 1,1, 1,1,1,1,1,1,1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Price'])
X_test = test_df[features]
y_test = np.log1p(test_df['Price'])

# ========== 8. 학습 ==========
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

# ========== 9. 평가 ==========
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
print(f"✓ MAPE: {mape:.1f}% (목표: ≤12%)")

errors = np.abs(actual - pred) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:10]:
    print(f"   {f}: {i:.4f}")

# ========== 10. 저장 ==========
joblib.dump(model, 'models/imported_v11.pkl')
joblib.dump(features, 'models/imported_v11_features.pkl')
joblib.dump({
    'model_enc': model_enc.to_dict(),
    'model_year_enc': model_year_enc.to_dict(),
    'model_year_mg_enc': model_year_mg_enc.to_dict(),
    'brand_enc': brand_enc.to_dict(),
}, 'models/imported_v11_encoders.pkl')
print("✅ 저장 완료!")

# ========== 11. 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_imported(name, year, mileage, opts=None, accident_free=1, grade='normal', 
                     brand='벤츠', brand_tier=4, class_rank=3):
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
        'Model_enc': model_enc.get(name, 5000),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, 5000)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, 5000)),
        'Brand_enc': brand_enc.get(brand, 5000),
        'Brand_Tier': brand_tier,
        'Class_Rank': class_rank,
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

print("\n1️⃣ 벤츠 클래스별 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for cls, rank in [('C-Class (W206)', 2), ('E-Class (W214)', 3), ('S-Class (W223)', 4)]:
    p = predict_imported(cls, 2022, 30000, {'has_leather_seat':1}, brand='벤츠', class_rank=rank)
    st = "✅" if p >= prev else "⚠️"
    print(f"   {cls:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n2️⃣ BMW 시리즈별 서열 (2022년 3만km):")
print("-"*60)
prev = 0
for series, rank in [('3시리즈 (G20)', 2), ('5시리즈 (G30)', 3), ('7시리즈 (G70)', 4)]:
    p = predict_imported(series, 2022, 30000, {'has_leather_seat':1}, brand='BMW', class_rank=rank)
    st = "✅" if p >= prev else "⚠️"
    print(f"   {series:20}: {p:,.0f}만원 {st}")
    prev = p

print("\n3️⃣ 옵션 효과 (E-Class 2022년 3만km):")
print("-"*60)
no_opt = predict_imported('E-Class (W214)', 2022, 30000, {}, brand='벤츠', class_rank=3)
full_opt = predict_imported('E-Class (W214)', 2022, 30000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1},
    brand='벤츠', class_rank=3)
diff = full_opt - no_opt
print(f"   노옵션: {no_opt:,.0f}만원")
print(f"   풀옵션: {full_opt:,.0f}만원")
print(f"   차이: +{diff:,.0f}만원 {'✅' if diff>0 else '❌'}")

print("\n4️⃣ 브랜드 간 비교 (E세그먼트 2022년 3만km):")
print("-"*60)
for brand, name, tier in [('벤츠', 'E-Class (W214)', 4), ('BMW', '5시리즈 (G30)', 4), ('아우디', 'A6 (C8)', 4)]:
    p = predict_imported(name, 2022, 30000, {'has_leather_seat':1}, brand=brand, brand_tier=tier, class_rank=3)
    print(f"   {brand} {name}: {p:,.0f}만원")

print("\n" + "="*70)
print("✅ 외제차 V11 완료!")
print("="*70)
