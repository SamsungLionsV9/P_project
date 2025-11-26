"""
개선된 모델 성능 평가
"""
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🔧 개선된 일반 국산차 모델 성능 평가")
print("="*80)

# 데이터 로드
df = pd.read_csv('data/processed_encar_combined.csv')

# 개선된 모델 로드
print("\n📦 개선된 모델 로딩...")
improved_model = joblib.load('models/regular_domestic_improved.pkl')
print("   ✓ 모델 로드 완료")

# 기존 모델도 로드
print("📦 기존 모델 로딩...")
original_model = joblib.load('models/regular_domestic_model.pkl')
print("   ✓ 모델 로드 완료")

# 피처 준비 함수들 (개선된 버전)
import re

def extract_generation(model_name):
    model_str = str(model_name)
    if '그랜저' in model_str:
        if 'GN7' in model_str or '더 뉴 그랜저' in model_str:
            return 'GN7'
        elif 'IG' in model_str:
            return 'IG'
        elif 'HG' in model_str:
            return 'HG'
    elif '쏘나타' in model_str:
        if 'DN8' in model_str or '디 엣지' in model_str:
            return 'DN8'
        elif 'LF' in model_str:
            return 'LF'
        elif 'YF' in model_str:
            return 'YF'
    elif '싼타페' in model_str:
        if 'MX5' in model_str or '5세대' in model_str:
            return 'MX5'
        elif 'TM' in model_str or '4세대' in model_str:
            return 'TM'
        elif 'DM' in model_str or '3세대' in model_str:
            return 'DM'
    elif '투싼' in model_str:
        if 'NX4' in model_str or '4세대' in model_str:
            return 'NX4'
        elif 'TL' in model_str or '3세대' in model_str:
            return 'TL'
    elif 'K5' in model_str:
        if 'DL3' in model_str or '3세대' in model_str:
            return 'DL3'
        elif 'JF' in model_str or '2세대' in model_str:
            return 'JF'
    elif '쏘렌토' in model_str:
        if '4세대' in model_str or 'MQ4' in model_str:
            return 'MQ4'
        elif '3세대' in model_str or 'UM' in model_str:
            return 'UM'
    elif '카니발' in model_str:
        if '4세대' in model_str or 'KA4' in model_str:
            return 'KA4'
        elif '3세대' in model_str:
            return 'KA3'
    return 'unknown'

def extract_trim_features(model_name, fuel):
    model_str = str(model_name).lower()
    features = {}
    features['is_hybrid'] = 1 if ('하이브리드' in model_str or '하이브리드' in fuel) else 0
    features['is_electric'] = 1 if ('전기' in model_str or '전기' in fuel) else 0
    features['is_premium_trim'] = 1 if any(x in model_str for x in ['프레스티지', '시그니처', '노블레스', '익스클루시브']) else 0
    features['is_sport'] = 1 if any(x in model_str for x in ['n라인', 'n-라인', '스포츠']) else 0
    features['is_large'] = 1 if any(x in model_str for x in ['롱바디', '7인승', '9인승', '11인승']) else 0
    return features

def prepare_improved_features(data):
    df = data.copy()
    current_year = 2025
    
    df['age'] = current_year - df['year']
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    df['age_group'] = pd.cut(df['age'], bins=[-1, 1, 2, 3, 5, 7, 100], labels=['1년', '2년', '3년', '3-5년', '5-7년', '7년+'])
    df['mileage_group'] = pd.cut(df['mileage'], bins=[-1, 30000, 60000, 100000, 150000, 999999], labels=['3만이하', '3-6만', '6-10만', '10-15만', '15만+'])
    
    df['generation'] = df['model_name'].apply(extract_generation)
    trim_features = df.apply(lambda x: extract_trim_features(x['model_name'], x['fuel']), axis=1)
    for key in ['is_hybrid', 'is_electric', 'is_premium_trim', 'is_sport', 'is_large']:
        df[key] = trim_features.apply(lambda x: x[key])
    
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts).fillna(1)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(2000)
    df['brand_avg_price'] = brand_price_mean
    model_price_mean = df.groupby('model_name')['price'].transform('mean').fillna(2000)
    df['model_avg_price'] = model_price_mean
    df['price_vs_model_avg'] = df['price'] / (model_price_mean + 1)
    
    df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
    df['is_overmileage'] = (df['mileage_per_year'] > 20000).astype(int)
    
    popular_models = ['그랜저', '아반떼', '쏘나타', 'K5', '싼타페', '투싼', '쏘렌토', '카니발', '스포티지', '코나']
    df['is_popular_model'] = df['model_name'].apply(lambda x: 1 if any(m in str(x) for m in popular_models) else 0)
    
    df['vehicle_type'] = 'sedan'
    suv_keywords = ['싼타페', '투싼', '쏘렌토', '스포티지', '셀토스', '코나', '팰리세이드', '모하비']
    mpv_keywords = ['카니발', '스타렉스', '스타리아']
    for keyword in suv_keywords:
        df.loc[df['model_name'].str.contains(keyword, na=False), 'vehicle_type'] = 'suv'
    for keyword in mpv_keywords:
        df.loc[df['model_name'].str.contains(keyword, na=False), 'vehicle_type'] = 'mpv'
    
    feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'mileage_group', 'generation',
                   'brand_fuel', 'vehicle_type', 'age', 'mileage', 'mileage_per_year',
                   'is_low_mileage', 'is_high_mileage', 'is_overmileage',
                   'model_popularity_log', 'brand_avg_price', 'model_avg_price',
                   'age_mileage_interaction', 'is_hybrid', 'is_electric', 'is_premium_trim', 
                   'is_sport', 'is_large', 'is_popular_model']
    
    return df[[f for f in feature_cols if f in df.columns]]

def prepare_original_features(data):
    df = data.copy()
    current_year = 2025
    df['age'] = current_year - df['year']
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    df['age_group'] = pd.cut(df['age'], bins=[-1, 1, 3, 5, 10, 100], labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts).fillna(1)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
    brand_price_mean = df.groupby('brand')['price'].transform('mean').fillna(2000)
    df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    feature_cols = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel', 'brand_price_tier',
                   'age', 'mileage', 'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
                   'model_popularity_log', 'age_mileage_interaction', 'is_eco']
    
    return df[[f for f in feature_cols if f in df.columns]]

# 테스트 케이스
test_cases = [
    {'brand': '현대', 'model': '그랜저'},
    {'brand': '현대', 'model': '아반떼'},
    {'brand': '현대', 'model': '싼타페'},
    {'brand': '기아', 'model': 'K5'},
    {'brand': '기아', 'model': '쏘렌토'},
    {'brand': '기아', 'model': '카니발'},
]

print("\n" + "="*80)
print("📋 모델 비교: 기존 vs 개선")
print("="*80)

comparison_results = []

for case in test_cases:
    brand = case['brand']
    model_pattern = case['model']
    
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
    
    test_samples = samples.sample(min(10, len(samples)), random_state=42)
    
    print(f"\n{'='*80}")
    print(f"🚗 {brand} {model_pattern}")
    print(f"{'='*80}")
    print(f"테스트 샘플: {len(test_samples)}개\n")
    
    original_errors = []
    improved_errors = []
    
    for idx, row in test_samples.iterrows():
        sample_df = pd.DataFrame([row])
        actual_price = row['price']
        
        # 기존 모델 예측
        features_orig = prepare_original_features(sample_df)
        log_pred_orig = original_model.predict(features_orig)[0]
        pred_orig = np.expm1(log_pred_orig)
        error_orig = abs(actual_price - pred_orig) / actual_price * 100
        original_errors.append(error_orig)
        
        # 개선 모델 예측
        features_imp = prepare_improved_features(sample_df)
        log_pred_imp = improved_model.predict(features_imp)[0]
        pred_imp = np.expm1(log_pred_imp)
        error_imp = abs(actual_price - pred_imp) / actual_price * 100
        improved_errors.append(error_imp)
        
        print(f"  {row['year']:.0f}년 | {row['mileage']:6.0f}km | 실제: {actual_price:5.0f}만원")
        print(f"    기존:  {pred_orig:5.0f}만원 (오차 {error_orig:4.1f}%)")
        print(f"    개선:  {pred_imp:5.0f}만원 (오차 {error_imp:4.1f}%) {'✅' if error_imp < error_orig else '❌'}")
    
    avg_orig = np.mean(original_errors)
    avg_imp = np.mean(improved_errors)
    improvement = ((avg_orig - avg_imp) / avg_orig) * 100
    
    print(f"\n  평균 오차:")
    print(f"    기존:  {avg_orig:5.2f}%")
    print(f"    개선:  {avg_imp:5.2f}% {'✅' if avg_imp < avg_orig else '❌'}")
    if improvement > 0:
        print(f"    개선율: {improvement:.1f}% 향상 ⚡")
    else:
        print(f"    변화: {-improvement:.1f}% 악화 ❌")
    
    comparison_results.append({
        'brand': brand,
        'model': model_pattern,
        'original_error': avg_orig,
        'improved_error': avg_imp,
        'improvement': improvement
    })

# 전체 요약
print("\n" + "="*80)
print("📊 전체 성능 비교")
print("="*80)

comp_df = pd.DataFrame(comparison_results)
print(f"\n기존 모델 평균 오차:  {comp_df['original_error'].mean():.2f}%")
print(f"개선 모델 평균 오차:  {comp_df['improved_error'].mean():.2f}%")
print(f"평균 개선율:         {comp_df['improvement'].mean():.1f}%")

print("\n개별 모델 성능:")
for _, row in comp_df.iterrows():
    status = "✅" if row['improvement'] > 0 else "❌"
    print(f"  {row['brand']:6s} {row['model']:10s}: "
          f"{row['original_error']:5.1f}% → {row['improved_error']:5.1f}% "
          f"({row['improvement']:+5.1f}%) {status}")

print("\n" + "="*80)
print("✅ 평가 완료!")
print("="*80)
