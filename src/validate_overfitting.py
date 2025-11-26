"""
과적합 검증 스크립트
- K-Fold Cross Validation
- Learning Curve 분석
- 실제 예측 샘플 확인
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold, learning_curve
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def validate_model(model_path, data_path, car_type):
    """
    모델 과적합 검증
    
    Args:
        model_path: 모델 파일 경로
        data_path: 데이터 파일 경로
        car_type: 'domestic' or 'imported'
    """
    print(f"\n{'='*70}")
    print(f"  🔍 {car_type.upper()} 모델 과적합 검증")
    print(f"{'='*70}")
    
    # Load model
    pipeline = joblib.load(model_path)
    print(f"  ✓ 모델 로드: {model_path}")
    
    # Load data
    df = pd.read_csv(data_path)
    df = df[df['car_type'] == car_type.capitalize()]
    
    # Feature engineering (간단 버전)
    current_year = 2025
    df['age'] = current_year - df['year']
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    df['log_price'] = np.log1p(df['price'])
    
    if car_type == 'domestic':
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
        brand_price_mean = df.groupby('brand')['price'].transform('mean')
        df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
        
        # Filter outliers
        df = df[df['price'] <= 5000]
    else:  # imported
        luxury_brands = ['벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 
                        '페라리', '람보르기니', '벤틀리', '롤스로이스', '맥라렌',
                        '마세라티', '애스턴마틴']
        df['is_luxury'] = df['brand'].isin(luxury_brands).astype(int)
        df['is_ultra_premium'] = (df['price'] > 5000).astype(int)
        brand_price_mean = df.groupby('brand')['price'].transform('mean')
        df['brand_value'] = brand_price_mean
        df['price_vs_brand_avg'] = df['price'] / (brand_price_mean + 1)
        df['model_rarity'] = 1 / (df['model_popularity'] + 1)
    
    print(f"  데이터: {len(df):,}건")
    
    # Prepare features
    categorical_features = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel']
    if car_type == 'domestic' and 'brand_price_tier' in df.columns:
        categorical_features.append('brand_price_tier')
    categorical_features = [f for f in categorical_features if f in df.columns]
    
    numerical_features = ['age', 'mileage', 'mileage_per_year', 
                         'is_low_mileage', 'model_popularity_log', 'is_eco']
    
    if car_type == 'domestic' and 'is_high_mileage' in df.columns:
        numerical_features.extend(['is_high_mileage', 'age_mileage_interaction'])
    elif car_type == 'imported' and 'is_luxury' in df.columns:
        numerical_features.extend(['is_luxury', 'is_ultra_premium', 'brand_value', 
                                   'price_vs_brand_avg', 'model_rarity'])
    
    numerical_features = [f for f in numerical_features if f in df.columns]
    
    feature_cols = categorical_features + numerical_features
    X = df[feature_cols]
    y = df['log_price']
    y_actual = df['price']
    
    # ---------------------------------------------------------
    # 1. K-Fold Cross Validation (과적합 핵심 검증)
    # ---------------------------------------------------------
    print(f"\n  📊 K-Fold Cross Validation (k=5)")
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # R² scores
    r2_scores = cross_val_score(pipeline, X, y, cv=kfold, scoring='r2', n_jobs=-1)
    print(f"     R² scores: {r2_scores}")
    print(f"     평균 R²: {r2_scores.mean():.4f} (±{r2_scores.std():.4f})")
    
    # MAE scores (negative로 나오므로 -1 곱함)
    mae_scores = -cross_val_score(pipeline, X, y, cv=kfold, 
                                   scoring='neg_mean_absolute_error', n_jobs=-1)
    
    # Log scale에서 실제 가격 scale로 변환
    mae_scores_actual = np.expm1(mae_scores)
    print(f"     MAE (만원): {mae_scores_actual}")
    print(f"     평균 MAE: {mae_scores_actual.mean():.0f}만원 (±{mae_scores_actual.std():.0f})")
    
    # ---------------------------------------------------------
    # 2. 과적합 판정
    # ---------------------------------------------------------
    print(f"\n  🔍 과적합 분석:")
    
    # Train vs CV 비교
    y_train_pred = pipeline.predict(X)
    y_train_pred_actual = np.expm1(y_train_pred)
    train_mae = mean_absolute_error(y_actual, y_train_pred_actual)
    train_r2 = r2_score(y_actual, y_train_pred_actual)
    
    cv_mae_mean = mae_scores_actual.mean()
    cv_r2_mean = r2_scores.mean()
    
    print(f"     Train MAE: {train_mae:.0f}만원")
    print(f"     CV MAE:    {cv_mae_mean:.0f}만원")
    print(f"     MAE 증가율: {(cv_mae_mean - train_mae) / train_mae * 100:.1f}%")
    
    print(f"\n     Train R²: {train_r2:.4f}")
    print(f"     CV R²:    {cv_r2_mean:.4f}")
    print(f"     R² 감소율: {(train_r2 - cv_r2_mean) / train_r2 * 100:.1f}%")
    
    # 과적합 판정 기준
    mae_increase = (cv_mae_mean - train_mae) / train_mae * 100
    r2_decrease = (train_r2 - cv_r2_mean) / train_r2 * 100
    
    print(f"\n  🎯 과적합 판정:")
    if mae_increase > 20 or r2_decrease > 5:
        print(f"     ⚠️  과적합 가능성 높음!")
        print(f"        - MAE 증가율 {mae_increase:.1f}% (기준: >20%)")
        print(f"        - R² 감소율 {r2_decrease:.1f}% (기준: >5%)")
        overfitting = True
    elif mae_increase > 10 or r2_decrease > 2:
        print(f"     ⚡ 경미한 과적합")
        print(f"        - MAE 증가율 {mae_increase:.1f}% (기준: 10-20%)")
        print(f"        - R² 감소율 {r2_decrease:.1f}% (기준: 2-5%)")
        overfitting = False
    else:
        print(f"     ✅ 과적합 없음 (양호)")
        print(f"        - MAE 증가율 {mae_increase:.1f}% (기준: <10%)")
        print(f"        - R² 감소율 {r2_decrease:.1f}% (기준: <2%)")
        overfitting = False
    
    # ---------------------------------------------------------
    # 3. 가격대별 성능 분석
    # ---------------------------------------------------------
    print(f"\n  💰 가격대별 예측 정확도:")
    
    y_pred_actual = np.expm1(pipeline.predict(X))
    
    price_ranges = [
        (0, 1000, "저가 (<1000만원)"),
        (1000, 3000, "중가 (1000-3000만원)"),
        (3000, 5000, "고가 (3000-5000만원)"),
        (5000, 10000, "초고가 (5000만원-1억)"),
        (10000, 999999, "슈퍼카 (1억+)")
    ]
    
    for min_p, max_p, label in price_ranges:
        mask = (y_actual >= min_p) & (y_actual < max_p)
        if mask.sum() == 0:
            continue
        
        subset_mae = mean_absolute_error(y_actual[mask], y_pred_actual[mask])
        subset_mape = np.mean(np.abs((y_actual[mask] - y_pred_actual[mask]) / y_actual[mask])) * 100
        print(f"     {label:25s}: MAE {subset_mae:6.0f}만원, MAPE {subset_mape:5.1f}%, N={mask.sum():,}")
    
    # ---------------------------------------------------------
    # 4. 샘플 예측 확인
    # ---------------------------------------------------------
    print(f"\n  📋 실제 vs 예측 샘플 (Random 10건):")
    sample_idx = np.random.choice(len(df), min(10, len(df)), replace=False)
    
    for idx in sample_idx:
        actual = y_actual.iloc[idx]
        pred = y_pred_actual[idx]
        error = abs(actual - pred)
        error_pct = error / actual * 100
        
        brand = df.iloc[idx]['brand']
        model = df.iloc[idx]['model_name']
        year = df.iloc[idx]['year']
        
        print(f"     {brand:8s} {model:15s} ({year:.0f}년): "
              f"실제 {actual:6.0f}만원 | 예측 {pred:6.0f}만원 | "
              f"오차 {error:5.0f}만원 ({error_pct:4.1f}%)")
    
    return {
        'car_type': car_type,
        'train_mae': train_mae,
        'cv_mae': cv_mae_mean,
        'train_r2': train_r2,
        'cv_r2': cv_r2_mean,
        'overfitting': overfitting
    }

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🔍 과적합 검증 시스템")
    print("="*70)
    
    results = []
    
    # Domestic model
    domestic_result = validate_model(
        '../models/domestic_car_price_model.pkl',
        '../data/processed_encar_combined.csv',
        'domestic'
    )
    results.append(domestic_result)
    
    # Imported model
    imported_result = validate_model(
        '../models/imported_car_price_model.pkl',
        '../data/processed_encar_combined.csv',
        'imported'
    )
    results.append(imported_result)
    
    # Summary
    print("\n" + "="*70)
    print("  📊 최종 과적합 검증 결과")
    print("="*70)
    
    summary_df = pd.DataFrame(results)
    print("\n" + summary_df.to_string(index=False))
    
    print("\n✅ 검증 완료!")
