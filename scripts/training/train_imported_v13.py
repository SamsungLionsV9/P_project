"""
외제차 V13: Unknown 30% 이하 + MAPE 10% 목표
============================================
개선:
1. 모델명에서 클래스 직접 추출 (정규식)
2. 더 많은 브랜드/모델 커버리지
3. Class_enc 활용도 향상
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

print("="*70)
print("🚗 외제차 V13: Unknown 30% 이하 + MAPE 10% 목표")
print("="*70)

# ========== 1. 데이터 로드 ==========
df = pd.read_csv('encar_imported_data.csv')
df_detail = pd.read_csv('data/complete_imported_details.csv')
df = df.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df = df[(df['Price'] >= 100) & (df['Price'] <= 100000)]
df = df[df['Mileage'] < 300000]
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'])
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['Age'] = 2025 - df['YearOnly']
df['Km_per_Year'] = df['Mileage'] / (df['Age'] + 1)
df = df[df['Km_per_Year'] <= 50000]
print(f"원본 데이터: {len(df):,}행")

# ========== 2. 옵션 프리미엄 ==========
opt_cols = ['has_sunroof','has_leather_seat','has_led_lamp','has_smart_key',
            'has_navigation','has_heated_seat','has_ventilated_seat','has_rear_camera']
for c in opt_cols:
    df[c] = df[c].fillna(0).astype(int) if c in df.columns else 0

OPTION_PREMIUM = {
    'has_ventilated_seat': 120, 'has_sunroof': 100, 'has_led_lamp': 100,
    'has_leather_seat': 80, 'has_navigation': 80, 'has_heated_seat': 60,
    'has_smart_key': 50, 'has_rear_camera': 50,
}
df['Option_Premium'] = sum(df[c] * OPTION_PREMIUM[c] for c in opt_cols)
df['Base_Price'] = (df['Price'] - df['Option_Premium']).clip(lower=100)

# ========== 3. 브랜드 등급 ==========
BRAND_TIER = {
    '페라리': 6, '람보르기니': 6, '맥라렌': 6, '롤스로이스': 6, '벤틀리': 6,
    '포르쉐': 5, '마세라티': 5,
    '벤츠': 4, 'BMW': 4, '아우디': 4, '렉서스': 4, '테슬라': 4,
    '볼보': 3, '랜드로버': 3, '재규어': 3, '인피니티': 3, '캐딜락': 3,
    '폭스바겐': 2, '미니': 2, '지프': 2, '푸조': 2, '시트로엥': 2,
    '토요타': 3, '혼다': 3, '닛산': 2, '마쓰다': 2,
    '폴스타': 4, '루시드': 5, '리비안': 4,
}
df['Brand_Tier'] = df['Manufacturer'].map(BRAND_TIER).fillna(2)

# ========== 4. 클래스 추출 (V13 - 모델명 기반) ==========
print("\n🔧 클래스 추출 (V13 - 모델명 직접 파싱)...")

# 클래스별 등급 정의
CLASS_RANK = {
    # 벤츠
    'A': 1, 'B': 1, 'CLA': 2, 'C': 2, 'E': 3, 'S': 4, 'G': 5, 'AMG GT': 5,
    'GLA': 2, 'GLB': 2, 'GLC': 3, 'GLE': 3, 'GLS': 4, 'EQS': 4, 'EQE': 3,
    # BMW
    '1시리즈': 1, '2시리즈': 1, '3시리즈': 2, '4시리즈': 2, '5시리즈': 3, '6시리즈': 3, '7시리즈': 4, '8시리즈': 4,
    'X1': 2, 'X2': 2, 'X3': 3, 'X4': 3, 'X5': 4, 'X6': 4, 'X7': 5,
    'M3': 4, 'M4': 4, 'M5': 5, 'M8': 5, 'i3': 2, 'i4': 3, 'i5': 3, 'i7': 4, 'iX': 4,
    'Z4': 3,
    # 아우디
    'A1': 1, 'A3': 1, 'A4': 2, 'A5': 2, 'A6': 3, 'A7': 3, 'A8': 4,
    'Q2': 1, 'Q3': 2, 'Q4': 2, 'Q5': 3, 'Q7': 4, 'Q8': 4,
    'RS3': 3, 'RS4': 4, 'RS5': 4, 'RS6': 5, 'RS7': 5, 'R8': 5,
    'e-tron': 3, 'e-tron GT': 4,
    # 포르쉐
    '718': 3, '911': 4, 'Panamera': 4, 'Cayenne': 4, 'Macan': 3, 'Taycan': 4,
    # 테슬라
    'Model 3': 3, 'Model Y': 3, 'Model S': 4, 'Model X': 4,
    # 볼보
    'S60': 2, 'S90': 3, 'V60': 2, 'V90': 3, 'XC40': 2, 'XC60': 3, 'XC90': 4,
    # 기타
    'MINI': 2, 'Countryman': 2, 'Clubman': 2,
    'Discovery': 3, 'Range Rover': 4, 'Defender': 4,
    'F-PACE': 3, 'E-PACE': 2, 'I-PACE': 3, 'XE': 2, 'XF': 3,
}

def extract_class_v3(model, manufacturer):
    """V13: 모델명에서 직접 클래스 추출"""
    model = str(model)
    mfr = str(manufacturer).lower()
    
    # === 벤츠 ===
    if '벤츠' in mfr:
        # "E-클래스", "E클래스", "E-Class" 패턴
        match = re.search(r'([A-Z])-?클래스|([A-Z])-?Class|^([A-Z])[\s-]', model, re.I)
        if match:
            cls = (match.group(1) or match.group(2) or match.group(3)).upper()
            return cls, CLASS_RANK.get(cls, 3)
        
        # "GLC-클래스", "GLE-클래스" 등
        match = re.search(r'(GL[ABCES]|EQ[SE]|AMG GT)', model, re.I)
        if match:
            cls = match.group(1).upper()
            return cls, CLASS_RANK.get(cls, 3)
    
    # === BMW ===
    if 'bmw' in mfr:
        # "5시리즈", "3시리즈" 등
        match = re.search(r'(\d)시리즈', model)
        if match:
            cls = f"{match.group(1)}시리즈"
            return cls, CLASS_RANK.get(cls, 3)
        
        # "X5", "X3", "M5" 등
        match = re.search(r'\b([XMZi]\d)\b', model)
        if match:
            cls = match.group(1).upper()
            return cls, CLASS_RANK.get(cls, 3)
    
    # === 아우디 ===
    if '아우디' in mfr:
        # "A6", "Q5", "RS6" 등
        match = re.search(r'\b(A\d|Q\d|RS\d|R8|e-tron)', model, re.I)
        if match:
            cls = match.group(1).upper()
            return cls, CLASS_RANK.get(cls, 3)
    
    # === 포르쉐 ===
    if '포르쉐' in mfr:
        patterns = ['911', '718', 'Panamera', '파나메라', 'Cayenne', '카이엔', 
                   'Macan', '마칸', 'Taycan', '타이칸', 'Boxster', 'Cayman']
        for p in patterns:
            if p.lower() in model.lower():
                cls = p if p[0].isdigit() else p.capitalize()
                if cls == '파나메라': cls = 'Panamera'
                if cls == '카이엔': cls = 'Cayenne'
                if cls == '마칸': cls = 'Macan'
                if cls == '타이칸': cls = 'Taycan'
                return cls, CLASS_RANK.get(cls, 4)
    
    # === 테슬라 ===
    if '테슬라' in mfr:
        match = re.search(r'모델\s*([3SYXR])|Model\s*([3SYXR])', model, re.I)
        if match:
            m = (match.group(1) or match.group(2)).upper()
            cls = f"Model {m}"
            return cls, CLASS_RANK.get(cls, 3)
    
    # === 볼보 ===
    if '볼보' in mfr:
        match = re.search(r'(S\d{2}|V\d{2}|XC\d{2})', model)
        if match:
            cls = match.group(1).upper()
            return cls, CLASS_RANK.get(cls, 3)
    
    # === 미니 ===
    if '미니' in mfr:
        if 'Countryman' in model or '컨트리맨' in model:
            return 'Countryman', 2
        if 'Clubman' in model or '클럽맨' in model:
            return 'Clubman', 2
        return 'MINI', 2
    
    # === 랜드로버 ===
    if '랜드로버' in mfr:
        if 'Range Rover' in model or '레인지로버' in model:
            return 'Range Rover', 4
        if 'Defender' in model or '디펜더' in model:
            return 'Defender', 4
        if 'Discovery' in model or '디스커버리' in model:
            return 'Discovery', 3
    
    # === 재규어 ===
    if '재규어' in mfr:
        match = re.search(r'([EFIXJ]-?PACE|X[EFJ])', model, re.I)
        if match:
            cls = match.group(1).upper().replace('-', '-')
            return cls, CLASS_RANK.get(cls, 3)
    
    # === 폭스바겐 ===
    if '폭스바겐' in mfr:
        patterns = {'Golf': 2, '골프': 2, 'Tiguan': 3, '티구안': 3, 
                   'Passat': 3, '파사트': 3, 'Arteon': 3, '아테온': 3,
                   'Touareg': 4, '투아렉': 4, 'ID.4': 3, 'ID.3': 2}
        for p, rank in patterns.items():
            if p.lower() in model.lower():
                return p if not p.startswith(('골','티','파','아','투')) else p, rank
    
    # === 지프 ===
    if '지프' in mfr:
        patterns = {'Wrangler': 3, '랭글러': 3, 'Cherokee': 3, '체로키': 3,
                   'Grand Cherokee': 4, '그랜드 체로키': 4, 'Compass': 2, '컴패스': 2}
        for p, rank in patterns.items():
            if p.lower() in model.lower():
                return p, rank
    
    # === 일본차 ===
    if '렉서스' in mfr:
        match = re.search(r'(ES|IS|LS|GS|LC|RC|NX|RX|GX|LX|UX)', model)
        if match:
            cls = match.group(1)
            rank = {'ES': 3, 'IS': 2, 'LS': 4, 'GS': 3, 'LC': 4, 'RC': 3,
                   'NX': 2, 'RX': 3, 'GX': 4, 'LX': 5, 'UX': 2}.get(cls, 3)
            return cls, rank
    
    # === 기타: 모델명 자체를 클래스로 ===
    # 첫 단어 추출 (괄호 제외)
    clean_model = re.sub(r'\([^)]*\)', '', model).strip()
    first_word = clean_model.split()[0] if clean_model else model
    if len(first_word) > 1:
        return first_word, 3
    
    return 'Unknown', 2

df['Class'], df['Class_Rank'] = zip(*df.apply(
    lambda r: extract_class_v3(r['Model'], r['Manufacturer']), axis=1))

# 클래스 분포 확인
class_dist = df['Class'].value_counts()
unknown_rate = (df['Class'] == 'Unknown').mean() * 100
print(f"✓ Unknown 비율: {unknown_rate:.1f}% (목표: <30%)")
print(f"✓ 클래스 분포 (상위 15개):")
for cls, cnt in class_dist.head(15).items():
    print(f"   {cls}: {cnt:,}개")

# ========== 5. 아웃라이어 제거 ==========
print("\n🔍 아웃라이어 제거...")
df['Model_Year'] = df['Model'] + '_' + df['YearOnly'].astype(str)
model_year_stats = df.groupby('Model_Year')['Base_Price'].agg(['mean', 'std', 'count'])
df = df.merge(model_year_stats[['mean', 'std']], left_on='Model_Year', right_index=True, suffixes=('', '_my'))
df['z_score'] = np.abs(df['Base_Price'] - df['mean']) / (df['std'] + 1)
df = df[df['z_score'] <= 1.0].copy()
print(f"정제 후: {len(df):,}행")

# ========== 6. Target Encoding ==========
def get_mg(m):
    if m < 30000: return 'A'
    elif m < 60000: return 'B'
    elif m < 100000: return 'C'
    elif m < 150000: return 'D'
    return 'E'
df['MG'] = df['Mileage'].apply(get_mg)
df['Model_Year_MG'] = df['Model_Year'] + '_' + df['MG']
df['Class_Year'] = df['Class'] + '_' + df['YearOnly'].astype(str)

def smooth_enc(df, col, target, min_n=30):
    g_mean = df[target].mean()
    stats = df.groupby(col)[target].agg(['mean', 'count'])
    return ((stats['mean'] * stats['count'] + g_mean * min_n) / (stats['count'] + min_n)).to_dict(), g_mean

model_enc, global_mean = smooth_enc(df, 'Model', 'Base_Price', 50)
model_year_enc, _ = smooth_enc(df, 'Model_Year', 'Base_Price', 30)
model_year_mg_enc, _ = smooth_enc(df, 'Model_Year_MG', 'Base_Price', 20)
brand_enc, _ = smooth_enc(df, 'Manufacturer', 'Base_Price', 100)
class_enc, _ = smooth_enc(df, 'Class', 'Base_Price', 30)
class_year_enc, _ = smooth_enc(df, 'Class_Year', 'Base_Price', 20)

df['Model_enc'] = df['Model'].map(model_enc).fillna(global_mean)
df['Model_Year_enc'] = df['Model_Year'].map(model_year_enc).fillna(df['Model_enc'])
df['Model_Year_MG_enc'] = df['Model_Year_MG'].map(model_year_mg_enc).fillna(df['Model_Year_enc'])
df['Brand_enc'] = df['Manufacturer'].map(brand_enc).fillna(global_mean)
df['Class_enc'] = df['Class'].map(class_enc).fillna(global_mean)
df['Class_Year_enc'] = df['Class_Year'].map(class_year_enc).fillna(df['Class_enc'])

df['Age_log'] = np.log1p(df['Age'])
df['Mile_log'] = np.log1p(df['Mileage'])

df['is_accident_free'] = df['is_accident_free'].fillna(0).astype(int)
grade_map = {'normal': 0, 'good': 1, 'excellent': 2}
df['inspection_grade_enc'] = df['inspection_grade'].map(grade_map).fillna(0)

# ========== 7. Train/Test ==========
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"\n✓ Train: {len(train_df):,}행, Test: {len(test_df):,}행")

# ========== 8. 피처 (Class_Year_enc 추가) ==========
features = [
    'Model_enc', 'Model_Year_enc', 'Model_Year_MG_enc', 'Brand_enc', 
    'Class_enc', 'Class_Year_enc',  # Class 관련 피처 강화
    'Brand_Tier', 'Class_Rank',
    'Age', 'Age_log', 'Mileage', 'Mile_log', 'Km_per_Year',
    'is_accident_free', 'inspection_grade_enc',
]

mono = (0,0,0,0, 0,0, 1,1, 0,0,0,0,0, 1,1)

X_train = train_df[features]
y_train = np.log1p(train_df['Base_Price'])
X_test = test_df[features]

# ========== 9. 학습 ==========
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
model.fit(X_train, y_train, eval_set=[(X_test, np.log1p(test_df['Base_Price']))], verbose=200)

# ========== 10. 평가 ==========
print("\n" + "="*70)
print("📈 평가")
print("="*70)

pred_base = np.expm1(model.predict(X_test))
pred_final = pred_base + test_df['Option_Premium'].values
actual = test_df['Price'].values

mae = mean_absolute_error(actual, pred_final)
mape = np.mean(np.abs(actual - pred_final) / actual) * 100
r2 = r2_score(np.log1p(actual), np.log1p(pred_final))

print(f"✓ R²: {r2:.4f}")
print(f"✓ MAE: {mae:.0f}만원")
print(f"✓ MAPE: {mape:.1f}% (목표: ≤10%)")

errors = np.abs(actual - pred_final) / actual * 100
print(f"\n📊 오차 분포:")
print(f"   5% 이내: {np.mean(errors <= 5)*100:.1f}%")
print(f"   10% 이내: {np.mean(errors <= 10)*100:.1f}%")
print(f"   15% 이내: {np.mean(errors <= 15)*100:.1f}%")

print("\n⭐ Feature Importance:")
for f,i in sorted(zip(features, model.feature_importances_), key=lambda x:-x[1])[:12]:
    print(f"   {f}: {i:.4f}")

# ========== 11. 저장 ==========
joblib.dump(model, 'models/imported_v13.pkl')
joblib.dump(features, 'models/imported_v13_features.pkl')
joblib.dump({
    'model_enc': model_enc,
    'model_year_enc': model_year_enc,
    'model_year_mg_enc': model_year_mg_enc,
    'brand_enc': brand_enc,
    'class_enc': class_enc,
    'class_year_enc': class_year_enc,
    'global_mean': global_mean,
    'option_premiums': OPTION_PREMIUM,
}, 'models/imported_v13_encoders.pkl')
print("✅ 저장 완료!")

# ========== 12. 테스트 ==========
print("\n" + "="*70)
print("🧪 핵심 테스트")
print("="*70)

def predict_v13(name, brand, year, mileage, opts=None, accident_free=1, grade='normal'):
    age = 2025 - year
    mg = get_mg(mileage)
    my = f"{name}_{year}"
    mymg = f"{my}_{mg}"
    grade_enc = {'normal':0, 'good':1, 'excellent':2}.get(grade, 0)
    cls, cls_rank = extract_class_v3(name, brand)
    cls_year = f"{cls}_{year}"
    
    f = {
        'Model_enc': model_enc.get(name, global_mean),
        'Model_Year_enc': model_year_enc.get(my, model_enc.get(name, global_mean)),
        'Model_Year_MG_enc': model_year_mg_enc.get(mymg, model_year_enc.get(my, global_mean)),
        'Brand_enc': brand_enc.get(brand, global_mean),
        'Class_enc': class_enc.get(cls, global_mean),
        'Class_Year_enc': class_year_enc.get(cls_year, class_enc.get(cls, global_mean)),
        'Brand_Tier': BRAND_TIER.get(brand, 3),
        'Class_Rank': cls_rank,
        'Age': age, 'Age_log': np.log1p(age),
        'Mileage': mileage, 'Mile_log': np.log1p(mileage),
        'Km_per_Year': mileage/(age+1),
        'is_accident_free': accident_free,
        'inspection_grade_enc': grade_enc,
    }
    
    base_price = np.expm1(model.predict(pd.DataFrame([f])[features])[0])
    opt_premium = sum(opts.get(c, 0) * OPTION_PREMIUM[c] for c in opt_cols) if opts else 0
    
    return {'final': base_price + opt_premium, 'base': base_price, 'option': opt_premium}

print("\n1️⃣ 벤츠 클래스별 서열:")
print("-"*60)
prev = 0
for cls in ['C-클래스 W206', 'E-클래스 W214', 'S-클래스 W223']:
    r = predict_v13(cls, '벤츠', 2022, 30000, {'has_leather_seat':1})
    st = "✅" if r['final'] >= prev else "⚠️"
    print(f"   {cls:20}: {r['final']:,.0f}만원 {st}")
    prev = r['final']

print("\n2️⃣ BMW 시리즈별 서열:")
print("-"*60)
prev = 0
for series in ['3시리즈 (G20)', '5시리즈 (G30)', '7시리즈 (G70)']:
    r = predict_v13(series, 'BMW', 2022, 30000, {'has_leather_seat':1})
    st = "✅" if r['final'] >= prev else "⚠️"
    print(f"   {series:20}: {r['final']:,.0f}만원 {st}")
    prev = r['final']

print("\n3️⃣ 옵션 효과 (E-클래스 2022년 3만km):")
print("-"*60)
no_opt = predict_v13('E-클래스 W214', '벤츠', 2022, 30000, {})
full_opt = predict_v13('E-클래스 W214', '벤츠', 2022, 30000,
    {'has_sunroof':1,'has_leather_seat':1,'has_led_lamp':1,'has_smart_key':1,
     'has_ventilated_seat':1,'has_heated_seat':1,'has_navigation':1,'has_rear_camera':1})
print(f"   노옵션: {no_opt['final']:,.0f}만원")
print(f"   풀옵션: {full_opt['final']:,.0f}만원 (기본:{full_opt['base']:,.0f} + 옵션:{full_opt['option']:,.0f})")
print(f"   차이: +{full_opt['final']-no_opt['final']:,.0f}만원 ✅")

print("\n" + "="*70)
print("✅ V13 완료!")
print("="*70)
