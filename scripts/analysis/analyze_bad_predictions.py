"""성능 저하 원인 분석"""
import pandas as pd
import numpy as np
import joblib

print("="*70)
print("🔍 성능 저하 원인 분석")
print("="*70)

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 패턴 이상치 제거
patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]

# 인코더 로드
encoders = joblib.load('models/domestic_v2_encoders.pkl')
mym_enc = encoders.get('Model_Year_Mileage_enc', {})

bad_models = [
    ('더 뉴 스파크', 2020, '310% 오차'),
    ('스포티지 5세대', 2021, '20% 오차'),
    ('베리 뉴 티볼리', 2021, '19% 오차'),
    ('더 K9', 2019, '17.5% 오차'),
    ('G80 (RG3)', 2022, '14% 오차'),
    ('토레스', 2022, '14.6% 오차'),
]

for model_name, year, error_desc in bad_models:
    print(f"\n{'='*70}")
    print(f"📊 {model_name} {year}년 ({error_desc})")
    print("-"*70)
    
    # 데이터 검색
    if model_name == '더 뉴 스파크':
        subset = df[(df['Model'].str.contains('스파크', na=False)) & (df['YearOnly']==year)]
    elif model_name == '베리 뉴 티볼리':
        subset = df[(df['Model'].str.contains('티볼리', na=False)) & (df['YearOnly']==year)]
    else:
        subset = df[(df['Model']==model_name) & (df['YearOnly']==year)]
    
    print(f"원본 데이터 개수: {len(subset)}")
    
    if len(subset) > 0:
        print(f"가격 분포:")
        print(f"  - min: {subset['Price'].min():,.0f}만원")
        print(f"  - Q25: {subset['Price'].quantile(0.25):,.0f}만원")
        print(f"  - median: {subset['Price'].median():,.0f}만원")
        print(f"  - Q75: {subset['Price'].quantile(0.75):,.0f}만원")
        print(f"  - max: {subset['Price'].max():,.0f}만원")
        print(f"  - std: {subset['Price'].std():,.0f}만원")
        
        # 가격 변동성 (CV)
        cv = subset['Price'].std() / subset['Price'].mean() * 100
        print(f"  - 변동계수(CV): {cv:.1f}%")
        
        # 모델명 변형 확인
        models_in_data = subset['Model'].unique()
        print(f"\n실제 모델명: {list(models_in_data)}")
    
    # 인코더에 있는지 확인
    search_term = model_name.replace('더 뉴 ', '').replace('베리 뉴 ', '')
    enc_keys = [k for k in mym_enc.keys() if search_term in k and str(year) in k]
    print(f"\n인코더 키 ({len(enc_keys)}개): {enc_keys[:5]}...")
    
    if len(enc_keys) == 0:
        print("⚠️ 문제: 인코더에 해당 키가 없음! → default 값 사용됨")

# 수입차도 분석
print("\n\n" + "="*70)
print("📊 수입차 성능 저하 분석")
print("="*70)

df_i = pd.read_csv('encar_imported_data.csv')
df_i_detail = pd.read_csv('data/complete_imported_details.csv')
df_i = df_i.merge(df_i_detail, left_on='Id', right_on='car_id', how='inner')
df_i['YearOnly'] = (df_i['Year'] // 100).astype(int)
df_i = df_i[~df_i['Price'].isin(patterns)]

encoders_i = joblib.load('models/imported_v2_encoders.pkl')
mym_enc_i = encoders_i.get('Model_Year_Mileage_enc', {})

bad_imported = [
    ('E-클래스 W213', 2019, '벤츠', '28.4% 오차'),
    ('미니 쿠퍼 S', 2023, '미니', '21.5% 오차'),
]

for model_name, year, brand, error_desc in bad_imported:
    print(f"\n{'-'*70}")
    print(f"📊 {brand} {model_name} {year}년 ({error_desc})")
    print("-"*70)
    
    subset = df_i[(df_i['Model']==model_name) & (df_i['YearOnly']==year)]
    print(f"데이터 개수: {len(subset)}")
    
    if len(subset) > 0:
        print(f"가격 분포:")
        print(f"  - min: {subset['Price'].min():,.0f}만원")
        print(f"  - median: {subset['Price'].median():,.0f}만원")
        print(f"  - max: {subset['Price'].max():,.0f}만원")
        print(f"  - std: {subset['Price'].std():,.0f}만원")
        
        cv = subset['Price'].std() / subset['Price'].mean() * 100
        print(f"  - 변동계수(CV): {cv:.1f}%")
    
    enc_keys = [k for k in mym_enc_i.keys() if model_name in k and str(year) in k]
    print(f"\n인코더 키 ({len(enc_keys)}개): {enc_keys[:5]}")

print("\n" + "="*70)
print("💡 성능 저하 주요 원인")
print("="*70)
print("""
1. 인코더 키 미존재: 학습 데이터에 없는 모델+연식+주행거리 조합
   → default 값 사용으로 부정확한 예측

2. 높은 가격 변동성 (CV > 30%): 
   → 같은 모델이라도 트림/옵션에 따라 가격 편차가 큼

3. 데이터 부족:
   → 특정 연식의 데이터가 적어 학습 불충분

4. 모델명 불일치:
   → API 요청 모델명과 학습 데이터 모델명이 다름
""")
