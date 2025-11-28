"""
국산차/수입차 분리 학습 시스템
- 각 차량 유형별 최적화된 모델 생성
- 고가 수입차도 이상치 제거 없이 학습
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plot style
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def create_features(df, car_type='domestic'):
    """
    차량 유형별 최적화된 피처 엔지니어링
    
    Args:
        df: DataFrame
        car_type: 'domestic' or 'imported'
    """
    print(f"  🔧 {car_type.upper()} 피처 생성 중...")
    
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # 공통 피처
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    
    # 연령 그룹
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    # 브랜드-연료 조합
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    
    # 모델 인기도
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    # 차량 유형별 특화 피처
    if car_type == 'domestic':
        # 국산차: 주행거리와 연식에 더 민감
        df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
        df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
        
        # 고급 브랜드 구분 (제네시스)
        df['is_premium_domestic'] = (df['brand'] == '제네시스').astype(int)
        
        # 제조사별 평균 가격 (시장 포지셔닝)
        brand_price_mean = df.groupby('brand')['price'].transform('mean')
        df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
        
    elif car_type == 'imported':
        # 수입차: 브랜드 프리미엄이 핵심
        luxury_brands = ['벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 
                        '페라리', '람보르기니', '벤틀리', '롤스로이스', '맥라렌',
                        '마세라티', '애스턴마틴']
        df['is_luxury'] = df['brand'].isin(luxury_brands).astype(int)
        
        # 고가 차량 구분 (5000만원 이상)
        df['is_ultra_premium'] = (df['price'] > 5000).astype(int)
        
        # 브랜드별 평균 가격 (브랜드 가치)
        brand_price_mean = df.groupby('brand')['price'].transform('mean')
        df['brand_value'] = brand_price_mean
        df['price_vs_brand_avg'] = df['price'] / (brand_price_mean + 1)
        
        # 희소성 (모델 개수가 적을수록 희소)
        df['model_rarity'] = 1 / (df['model_popularity'] + 1)
    
    # 전기/하이브리드
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    # 가격 로그 변환 (타겟)
    df['log_price'] = np.log1p(df['price'])
    
    print(f"     ✓ 생성된 피처 수: {len([c for c in df.columns if c not in ['price', 'log_price']])}")
    
    return df

def train_single_model(df, car_type, model_path):
    """
    단일 차량 유형 모델 학습
    
    Args:
        df: DataFrame (해당 차량 유형만)
        car_type: 'domestic' or 'imported'
        model_path: 저장 경로
    """
    print(f"\n{'='*70}")
    print(f"  📚 {car_type.upper()} MODEL TRAINING")
    print(f"{'='*70}")
    print(f"  데이터 크기: {len(df):,}건")
    
    # 피처 엔지니어링
    df = create_features(df, car_type)
    
    # 이상치 제거 전략
    if car_type == 'domestic':
        # 국산차: 명확한 오류 데이터만 제거
        # 제네시스 G90 신차가 1억 이상이므로, 2억 이하는 정상으로 간주
        price_threshold = 20000  # 2억원
        initial_count = len(df)
        
        # 극단적 이상치만 제거 (명백한 입력 오류)
        df = df[df['price'] <= price_threshold]
        
        # 추가: 가격이 너무 낮은 것도 제거 (100만원 이하는 오류일 가능성)
        df = df[df['price'] >= 100]
        
        removed = initial_count - len(df)
        print(f"  🧹 극단 이상치 제거: {removed:,}건 (100만원 미만 또는 {price_threshold:,}만원 초과)")
        print(f"  ℹ️  제네시스 등 고급 국산차 포함 (정상 데이터)")
    else:
        # 수입차: 이상치 제거 안 함 (고가 차량도 유효 데이터)
        print(f"  ℹ️  수입차는 이상치 제거 없음 (고가 차량 포함)")
    
    print(f"  최종 데이터: {len(df):,}건")
    print(f"  가격 범위: {df['price'].min():.0f}만원 ~ {df['price'].max():.0f}만원")
    
    # Train/Test split
    categorical_features = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel']
    if car_type == 'domestic' and 'brand_price_tier' in df.columns:
        categorical_features.append('brand_price_tier')
    
    # 존재하는 컬럼만 선택
    categorical_features = [f for f in categorical_features if f in df.columns]
    
    numerical_features = ['age', 'mileage', 'mileage_per_year', 
                         'is_low_mileage', 'model_popularity_log', 'is_eco']
    
    # 차량 유형별 추가 피처
    if car_type == 'domestic' and 'is_high_mileage' in df.columns:
        numerical_features.extend(['is_high_mileage', 'age_mileage_interaction', 'is_premium_domestic'])
    elif car_type == 'imported' and 'is_luxury' in df.columns:
        numerical_features.extend(['is_luxury', 'is_ultra_premium', 'brand_value', 
                                   'price_vs_brand_avg', 'model_rarity'])
    
    # 존재하는 컬럼만 선택
    numerical_features = [f for f in numerical_features if f in df.columns]
    
    feature_cols = categorical_features + numerical_features
    X = df[feature_cols]
    y = df['log_price']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n  📊 Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )
    
    # XGBoost 하이퍼파라미터 (차량 유형별 최적화)
    if car_type == 'domestic':
        xgb_params = {
            'n_estimators': 1000,
            'learning_rate': 0.05,
            'max_depth': 7,
            'min_child_weight': 3,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'objective': 'reg:squarederror',
            'random_state': 42,
            'n_jobs': -1
        }
    else:  # imported
        xgb_params = {
            'n_estimators': 1500,  # 더 많은 트리
            'learning_rate': 0.03,  # 더 느린 학습
            'max_depth': 8,  # 더 깊은 트리 (복잡한 패턴)
            'min_child_weight': 1,  # 더 세밀한 분할
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'objective': 'reg:squarederror',
            'random_state': 42,
            'n_jobs': -1
        }
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', XGBRegressor(**xgb_params))
    ])
    
    # Train
    print(f"\n  🚀 모델 학습 중...")
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    # Convert back from log
    y_train_actual = np.expm1(y_train)
    y_test_actual = np.expm1(y_test)
    y_train_pred_actual = np.expm1(y_train_pred)
    y_test_pred_actual = np.expm1(y_test_pred)
    
    # Metrics
    train_mae = mean_absolute_error(y_train_actual, y_train_pred_actual)
    test_mae = mean_absolute_error(y_test_actual, y_test_pred_actual)
    train_r2 = r2_score(y_train_actual, y_train_pred_actual)
    test_r2 = r2_score(y_test_actual, y_test_pred_actual)
    
    # MAPE
    train_mape = np.mean(np.abs((y_train_actual - y_train_pred_actual) / y_train_actual)) * 100
    test_mape = np.mean(np.abs((y_test_actual - y_test_pred_actual) / y_test_actual)) * 100
    
    print(f"\n  📈 성능 지표:")
    print(f"     Train MAE: {train_mae:.0f}만원 | MAPE: {train_mape:.2f}%")
    print(f"     Test MAE:  {test_mae:.0f}만원 | MAPE: {test_mape:.2f}%")
    print(f"     Train R²:  {train_r2:.4f}")
    print(f"     Test R²:   {test_r2:.4f}")
    
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\n  ✅ 모델 저장: {model_path}")
    
    # Save metrics
    metrics = {
        'car_type': car_type,
        'data_count': len(df),
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mape': train_mape,
        'test_mape': test_mape,
        'price_min': df['price'].min(),
        'price_max': df['price'].max(),
        'price_mean': df['price'].mean()
    }
    
    return pipeline, metrics, (X_test, y_test_actual, y_test_pred_actual)

def train_separated_models(combined_data_path='../data/processed_encar_combined.csv'):
    """
    국산차/수입차 분리 학습 메인 함수
    """
    print("\n" + "="*70)
    print("  🚗 국산차/수입차 분리 학습 시스템")
    print("="*70)
    
    # Load data
    print("\n📂 통합 데이터 로딩...")
    df = pd.read_csv(combined_data_path)
    print(f"   전체 데이터: {len(df):,}건")
    
    # Split by car type
    df_domestic = df[df['car_type'] == 'Domestic'].copy()
    df_imported = df[df['car_type'] == 'Imported'].copy()
    
    print(f"   국산차: {len(df_domestic):,}건")
    print(f"   수입차: {len(df_imported):,}건")
    
    # Train domestic model
    domestic_model, domestic_metrics, domestic_test = train_single_model(
        df_domestic, 
        'domestic',
        '../models/domestic_car_price_model.pkl'
    )
    
    # Train imported model
    imported_model, imported_metrics, imported_test = train_single_model(
        df_imported,
        'imported', 
        '../models/imported_car_price_model.pkl'
    )
    
    # Summary comparison
    print("\n" + "="*70)
    print("  📊 모델 비교 요약")
    print("="*70)
    
    comparison = pd.DataFrame([domestic_metrics, imported_metrics])
    comparison = comparison[['car_type', 'data_count', 'test_mae', 'test_mape', 'test_r2', 'price_mean', 'price_max']]
    comparison.columns = ['차량유형', '데이터수', 'MAE(만원)', 'MAPE(%)', 'R²', '평균가격', '최고가격']
    print("\n" + comparison.to_string(index=False))
    
    # Save comparison
    comparison.to_csv('../models/separated_models_comparison.csv', index=False, encoding='utf-8-sig')
    print(f"\n  ✅ 비교표 저장: ../models/separated_models_comparison.csv")
    
    print("\n" + "="*70)
    print("  🎉 분리 학습 완료!")
    print("="*70)
    print("\n  📁 생성된 모델:")
    print("     1. domestic_car_price_model.pkl (국산차)")
    print("     2. imported_car_price_model.pkl (수입차)")
    print("     3. separated_models_comparison.csv (비교표)")

if __name__ == "__main__":
    train_separated_models()
