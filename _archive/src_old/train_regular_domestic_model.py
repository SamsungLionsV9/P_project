"""
일반 국산차 전용 모델 학습 (제네시스 제외)
- 현대, 기아, 쉐보레, KG모빌리티, 르노코리아 등
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib
import os

def create_regular_features(df):
    """일반 국산차 피처 엔지니어링"""
    print("  🔧 일반 국산차 피처 생성 중...")
    
    current_year = 2025
    df['age'] = current_year - df['year']
    
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
    
    brand_price_mean = df.groupby('brand')['price'].transform('mean')
    df['brand_price_tier'] = pd.cut(brand_price_mean, bins=3, labels=['budget', 'mid', 'premium'])
    
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    df['log_price'] = np.log1p(df['price'])
    
    print(f"     ✓ 생성된 피처 수: {len([c for c in df.columns if c not in ['price', 'log_price']])}")
    
    return df

def train_regular_domestic_model(data_path='../data/processed_encar_combined.csv',
                                 model_path='../models/regular_domestic_model.pkl'):
    """일반 국산차 모델 학습"""
    
    print("\n" + "="*70)
    print("  🚗 일반 국산차 모델 학습 (제네시스 제외)")
    print("="*70)
    
    # 데이터 로드
    print("\n  📂 데이터 로딩...")
    df = pd.read_csv(data_path)
    
    # 국산차 중 제네시스 제외
    df = df[(df['car_type'] == 'Domestic') & (df['brand'] != '제네시스')].copy()
    print(f"     일반 국산차 데이터: {len(df):,}건")
    
    # 피처 엔지니어링
    df = create_regular_features(df)
    
    # 이상치 제거
    initial_count = len(df)
    df = df[(df['price'] >= 100) & (df['price'] <= 8000)]  # 100만~8000만원
    removed = initial_count - len(df)
    print(f"  🧹 이상치 제거: {removed:,}건 (100만원 미만 또는 8000만원 초과)")
    print(f"  최종 데이터: {len(df):,}건")
    print(f"  가격 범위: {df['price'].min():.0f}만원 ~ {df['price'].max():.0f}만원")
    
    # 피처 선택
    categorical_features = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel', 'brand_price_tier']
    numerical_features = [
        'age', 'mileage', 'mileage_per_year',
        'is_low_mileage', 'is_high_mileage',
        'model_popularity_log', 'age_mileage_interaction', 'is_eco'
    ]
    
    categorical_features = [f for f in categorical_features if f in df.columns]
    numerical_features = [f for f in numerical_features if f in df.columns]
    
    feature_cols = categorical_features + numerical_features
    X = df[feature_cols]
    y = df['log_price']
    
    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n  📊 Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )
    
    # 하이퍼파라미터
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
    
    # Pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', XGBRegressor(**xgb_params))
    ])
    
    # 학습
    print(f"\n  🚀 모델 학습 중...")
    pipeline.fit(X_train, y_train)
    
    # 예측
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    y_train_actual = np.expm1(y_train)
    y_test_actual = np.expm1(y_test)
    y_train_pred_actual = np.expm1(y_train_pred)
    y_test_pred_actual = np.expm1(y_test_pred)
    
    # 평가
    train_mae = mean_absolute_error(y_train_actual, y_train_pred_actual)
    test_mae = mean_absolute_error(y_test_actual, y_test_pred_actual)
    train_r2 = r2_score(y_train_actual, y_train_pred_actual)
    test_r2 = r2_score(y_test_actual, y_test_pred_actual)
    
    train_mape = np.mean(np.abs((y_train_actual - y_train_pred_actual) / y_train_actual)) * 100
    test_mape = np.mean(np.abs((y_test_actual - y_test_pred_actual) / y_test_actual)) * 100
    
    print(f"\n  📈 성능 지표:")
    print(f"     Train MAE: {train_mae:.0f}만원 | MAPE: {train_mape:.2f}%")
    print(f"     Test MAE:  {test_mae:.0f}만원 | MAPE: {test_mape:.2f}%")
    print(f"     Train R²:  {train_r2:.4f}")
    print(f"     Test R²:   {test_r2:.4f}")
    
    # Cross Validation
    print(f"\n  🔄 K-Fold Cross Validation (k=5)...")
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=kfold, scoring='r2', n_jobs=-1)
    print(f"     CV R² scores: {cv_scores}")
    print(f"     평균 CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    r2_gap = abs(train_r2 - cv_scores.mean())
    if r2_gap < 0.05:
        print(f"     ✅ 과적합 없음 (Train-CV 차이: {r2_gap:.4f})")
    else:
        print(f"     ⚠️  과적합 가능성 (Train-CV 차이: {r2_gap:.4f})")
    
    # 모델 저장
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\n  ✅ 모델 저장: {model_path}")
    
    return {
        'data_count': len(df),
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'cv_r2': cv_scores.mean(),
        'test_mape': test_mape
    }

if __name__ == "__main__":
    result = train_regular_domestic_model()
    
    print("\n" + "="*70)
    print("  🎉 일반 국산차 모델 학습 완료!")
    print("="*70)
