"""
브랜드별 대표 차종 예측 테스트
3-Model 시스템 성능 검증
"""
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🚗 브랜드별 대표 차종 예측 테스트")
print("="*80)

# 데이터 로드
df = pd.read_csv('data/processed_encar_combined.csv')

# 모델 로드
print("\n📦 모델 로딩...")
regular_model = joblib.load('models/regular_domestic_model.pkl')
genesis_model = joblib.load('models/genesis_car_price_model.pkl')
imported_model = joblib.load('models/imported_car_price_model.pkl')
print("   ✓ 3개 모델 로드 완료")

def prepare_features(data, model_type):
    """피처 준비"""
    df = data.copy()
    current_year = 2025
    
    df['age'] = current_year - df['year']
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts).fillna(1)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    if model_type == 'regular_domestic':
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
        df['brand_fuel'] = df['brand'] + '_' + df['fuel']
        
        brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(2000)
        df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
        
        feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel', 'brand_price_tier',
                       'age', 'mileage', 'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                       'model_popularity_log', 'age_mileage_interaction', 'is_eco']
    
    elif model_type == 'genesis':
        df['is_high_mileage'] = (df['mileage'] > 100000).astype(int)
        df['model_tier'] = 'mid'
        df.loc[df['model_name'].str.contains('G70|GV70', na=False), 'model_tier'] = 'entry'
        df.loc[df['model_name'].str.contains('G90|GV90', na=False), 'model_tier'] = 'luxury'
        df['is_suv'] = df['model_name'].str.contains('GV', na=False).astype(int)
        
        model_price_map = {'G70': 4500, 'G80': 5500, 'G90': 9000,
                          'GV70': 5000, 'GV80': 6500, 'GV90': 10000}
        def get_base_price(model_name):
            for key, price in model_price_map.items():
                if key in str(model_name):
                    return price
            return 5000
        df['model_base_price'] = df['model_name'].apply(get_base_price)
        
        df['depreciation_rate'] = (1 - (df['age'] * 0.12)).clip(0.3, 1.0)
        df['rarity_score'] = 1 / (df['model_popularity'] + 1)
        
        model_price_mean = df.groupby('model_name')['price'].transform('mean').fillna(5000)
        df['is_high_trim'] = (df['price'] > model_price_mean * 1.1).astype(int)
        
        df['condition_score'] = (df['mileage_per_year'] / 15000).clip(0, 3)
        
        feature_cols = ['model_name', 'fuel', 'age_group', 'model_tier',
                       'age', 'mileage', 'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                       'model_popularity_log', 'is_suv', 'model_base_price',
                       'depreciation_rate', 'rarity_score', 'is_high_trim', 'is_eco', 'condition_score']
    
    else:  # imported
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        df['brand_fuel'] = df['brand'] + '_' + df['fuel']
        
        luxury_brands = ['벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 
                        '페라리', '람보르기니', '벤틀리', '롤스로이스', '맥라렌',
                        '마세라티', '애스턴마틴']
        df['is_luxury'] = df['brand'].isin(luxury_brands).astype(int)
        df['is_ultra_premium'] = (df['price'] > 5000).astype(int)
        
        brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(5000)
        df['brand_value'] = brand_price_mean
        df['price_vs_brand_avg'] = df['price'] / (brand_price_mean + 1)
        df['model_rarity'] = 1 / (df['model_popularity'] + 1)
        
        feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel',
                       'age', 'mileage', 'mileage_per_year', 'is_low_mileage',
                       'model_popularity_log', 'is_eco', 'is_luxury', 'is_ultra_premium',
                       'brand_value', 'price_vs_brand_avg', 'model_rarity']
    
    feature_cols = [f for f in feature_cols if f in df.columns]
    return df[feature_cols]

def predict_sample(sample, model, model_type):
    """단일 샘플 예측"""
    features = prepare_features(sample, model_type)
    log_pred = model.predict(features)[0]
    return np.expm1(log_pred)

# 테스트할 브랜드별 대표 차종
test_cases = [
    # 일반 국산차
    {'brand': '현대', 'model': '그랜저', 'category': '일반 국산차'},
    {'brand': '현대', 'model': '아반떼', 'category': '일반 국산차'},
    {'brand': '현대', 'model': '싼타페', 'category': '일반 국산차'},
    {'brand': '기아', 'model': 'K5', 'category': '일반 국산차'},
    {'brand': '기아', 'model': '쏘렌토', 'category': '일반 국산차'},
    {'brand': '기아', 'model': '카니발', 'category': '일반 국산차'},
    
    # 제네시스
    {'brand': '제네시스', 'model': 'G70', 'category': '제네시스'},
    {'brand': '제네시스', 'model': 'G80', 'category': '제네시스'},
    {'brand': '제네시스', 'model': 'GV80', 'category': '제네시스'},
    
    # 수입차
    {'brand': 'BMW', 'model': '3시리즈', 'category': '수입차'},
    {'brand': 'BMW', 'model': '5시리즈', 'category': '수입차'},
    {'brand': '벤츠', 'model': 'E-클래스', 'category': '수입차'},
    {'brand': '벤츠', 'model': 'C-클래스', 'category': '수입차'},
    {'brand': '아우디', 'model': 'A4', 'category': '수입차'},
    {'brand': '테슬라', 'model': '모델 3', 'category': '수입차'},
    {'brand': '포르쉐', 'model': '카이엔', 'category': '수입차'},
]

print("\n" + "="*80)
print("📋 브랜드별 대표 차종 예측 결과")
print("="*80)

results = []

for case in test_cases:
    brand = case['brand']
    model_pattern = case['model']
    category = case['category']
    
    # 해당 브랜드/모델 샘플 찾기 (2020~2023년, 주행거리 3~10만km)
    samples = df[
        (df['brand'] == brand) &
        (df['model_name'].str.contains(model_pattern, na=False)) &
        (df['year'] >= 2020) &
        (df['year'] <= 2023) &
        (df['mileage'] >= 30000) &
        (df['mileage'] <= 100000)
    ]
    
    if len(samples) < 5:
        continue
    
    # 랜덤 샘플 5개 선택
    test_samples = samples.sample(min(5, len(samples)), random_state=42)
    
    print(f"\n{'='*80}")
    print(f"🚗 {brand} {model_pattern} ({category})")
    print(f"{'='*80}")
    
    # 모델 선택
    if category == '일반 국산차':
        model = regular_model
        model_type = 'regular_domestic'
        model_name = '일반 국산차 모델'
    elif category == '제네시스':
        model = genesis_model
        model_type = 'genesis'
        model_name = '제네시스 모델'
    else:
        model = imported_model
        model_type = 'imported'
        model_name = '수입차 모델'
    
    print(f"사용 모델: {model_name}")
    print(f"테스트 샘플: {len(test_samples)}개\n")
    
    errors = []
    for idx, row in test_samples.iterrows():
        sample_df = pd.DataFrame([row])
        
        actual_price = row['price']
        predicted_price = predict_sample(sample_df, model, model_type)
        
        error = abs(actual_price - predicted_price)
        error_pct = (error / actual_price) * 100
        errors.append(error_pct)
        
        print(f"  {row['year']:.0f}년 | {row['mileage']:6.0f}km | "
              f"실제: {actual_price:5.0f}만원 | 예측: {predicted_price:5.0f}만원 | "
              f"오차: {error:4.0f}만원 ({error_pct:4.1f}%)")
    
    avg_error = np.mean(errors)
    print(f"\n  평균 오차율: {avg_error:.2f}%")
    
    results.append({
        'brand': brand,
        'model': model_pattern,
        'category': category,
        'avg_error': avg_error,
        'count': len(test_samples)
    })

# 요약
print("\n" + "="*80)
print("📊 카테고리별 평균 오차율")
print("="*80)

results_df = pd.DataFrame(results)

print("\n[일반 국산차]")
domestic_results = results_df[results_df['category'] == '일반 국산차']
if len(domestic_results) > 0:
    for _, row in domestic_results.iterrows():
        print(f"  {row['brand']:6s} {row['model']:10s}: {row['avg_error']:5.2f}%")
    print(f"  평균: {domestic_results['avg_error'].mean():.2f}%")

print("\n[제네시스]")
genesis_results = results_df[results_df['category'] == '제네시스']
if len(genesis_results) > 0:
    for _, row in genesis_results.iterrows():
        print(f"  {row['brand']:6s} {row['model']:10s}: {row['avg_error']:5.2f}%")
    print(f"  평균: {genesis_results['avg_error'].mean():.2f}%")

print("\n[수입차]")
imported_results = results_df[results_df['category'] == '수입차']
if len(imported_results) > 0:
    for _, row in imported_results.iterrows():
        print(f"  {row['brand']:6s} {row['model']:10s}: {row['avg_error']:5.2f}%")
    print(f"  평균: {imported_results['avg_error'].mean():.2f}%")

print("\n" + "="*80)
print("✅ 테스트 완료!")
print("="*80)

# 성능 등급
overall_avg = results_df['avg_error'].mean()
print(f"\n전체 평균 오차율: {overall_avg:.2f}%")

if overall_avg < 5:
    grade = "S급 (완벽)"
elif overall_avg < 10:
    grade = "A급 (우수)"
elif overall_avg < 15:
    grade = "B급 (양호)"
elif overall_avg < 20:
    grade = "C급 (보통)"
else:
    grade = "D급 (개선 필요)"

print(f"성능 등급: {grade}")
