"""
제네시스 전용 모델 학습
- 프리미엄 국산차 브랜드 특화
- 브랜드 프리미엄 반영
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

def create_genesis_features(df):
    """제네시스 특화 피처 엔지니어링"""
    print("  🔧 제네시스 전용 피처 생성 중...")
    
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # 기본 피처
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 100000).astype(int)
    
    # 연령 그룹
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    # 모델 인기도
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    # 제네시스 특화 피처
    
    # 1. 모델 티어 (G70 < G80 < G90)
    df['model_tier'] = 'mid'
    df.loc[df['model_name'].str.contains('G70|GV70', na=False), 'model_tier'] = 'entry'
    df.loc[df['model_name'].str.contains('G90|GV90', na=False), 'model_tier'] = 'luxury'
    
    # 2. SUV vs 세단
    df['is_suv'] = df['model_name'].str.contains('GV', na=False).astype(int)
    
    # 3. 가격대별 구분
    # 제네시스는 신차 가격이 명확함
    model_price_map = {
        'G70': 4500,
        'G80': 5500,
        'G90': 9000,
        'GV70': 5000,
        'GV80': 6500,
        'GV90': 10000
    }
    
    def get_base_price(model_name):
        for key, price in model_price_map.items():
            if key in str(model_name):
                return price
        return 5000  # default
    
    df['model_base_price'] = df['model_name'].apply(get_base_price)
    
    # 4. 감가상각률 (나이별)
    # 제네시스는 일반 국산차보다 가치 유지 잘됨
    df['depreciation_rate'] = 1 - (df['age'] * 0.12)  # 년당 12% 감가
    df['depreciation_rate'] = df['depreciation_rate'].clip(0.3, 1.0)
    
    # 5. 희소성 (적을수록 희소)
    df['rarity_score'] = 1 / (df['model_popularity'] + 1)
    
    # 6. 럭셔리 옵션 추정 (가격이 모델 평균보다 높으면 풀옵)
    model_price_mean = df.groupby('model_name')['price'].transform('mean')
    df['is_high_trim'] = (df['price'] > model_price_mean * 1.1).astype(int)
    
    # 7. 연료 효율 (하이브리드/전기)
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    # 8. 상태 지표 (주행거리 vs 연식)
    df['condition_score'] = df['mileage_per_year'] / 15000  # 년 15,000km 기준
    df['condition_score'] = df['condition_score'].clip(0, 3)
    
    # 로그 변환 (타겟)
    df['log_price'] = np.log1p(df['price'])
    
    print(f"     ✓ 생성된 피처 수: {len([c for c in df.columns if c not in ['price', 'log_price']])}")
    
    return df

def train_genesis_model(data_path='../data/processed_encar_combined.csv',
                       model_path='../models/genesis_car_price_model.pkl'):
    """제네시스 모델 학습"""
    
    print("\n" + "="*70)
    print("  🏆 제네시스 전용 모델 학습")
    print("="*70)
    
    # 데이터 로드
    print("\n  📂 데이터 로딩...")
    df = pd.read_csv(data_path)
    
    # 제네시스만 필터링
    df = df[df['brand'] == '제네시스'].copy()
    print(f"     제네시스 데이터: {len(df):,}건")
    
    # 피처 엔지니어링
    df = create_genesis_features(df)
    
    # 이상치 제거 (극단적인 경우만)
    initial_count = len(df)
    df = df[(df['price'] >= 500) & (df['price'] <= 20000)]  # 500만~2억
    removed = initial_count - len(df)
    print(f"  🧹 극단 이상치 제거: {removed:,}건")
    print(f"  최종 데이터: {len(df):,}건")
    print(f"  가격 범위: {df['price'].min():.0f}만원 ~ {df['price'].max():.0f}만원")
    
    # 피처 선택
    categorical_features = ['model_name', 'fuel', 'age_group', 'model_tier']
    numerical_features = [
        'age', 'mileage', 'mileage_per_year',
        'is_low_mileage', 'is_high_mileage',
        'model_popularity_log', 'is_suv',
        'model_base_price', 'depreciation_rate',
        'rarity_score', 'is_high_trim',
        'is_eco', 'condition_score'
    ]
    
    # 존재하는 컬럼만
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
    
    # 제네시스 최적화 하이퍼파라미터
    xgb_params = {
        'n_estimators': 1200,      # 중간 데이터 크기에 적합
        'learning_rate': 0.04,     # 천천히 학습
        'max_depth': 6,            # 과적합 방지
        'min_child_weight': 2,
        'subsample': 0.85,
        'colsample_bytree': 0.85,
        'gamma': 0.1,              # 과적합 방지
        'reg_alpha': 0.1,          # L1 규제
        'reg_lambda': 1.0,         # L2 규제
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
    
    # 로그 스케일에서 원래 스케일로
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
    
    # 과적합 검사
    r2_gap = abs(train_r2 - cv_scores.mean())
    if r2_gap < 0.05:
        print(f"     ✅ 과적합 없음 (Train-CV 차이: {r2_gap:.4f})")
    else:
        print(f"     ⚠️  과적합 가능성 (Train-CV 차이: {r2_gap:.4f})")
    
    # 모델 저장
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\n  ✅ 모델 저장: {model_path}")
    
    # 샘플 예측
    print(f"\n  📋 예측 샘플 (Random 10건):")
    sample_idx = np.random.choice(len(X_test), min(10, len(X_test)), replace=False)
    
    for i, idx in enumerate(sample_idx):
        actual = y_test_actual.iloc[idx]
        pred = y_test_pred_actual[idx]
        error = abs(actual - pred)
        error_pct = error / actual * 100
        
        model = df.iloc[X_test.index[idx]]['model_name']
        year = df.iloc[X_test.index[idx]]['year']
        mileage = df.iloc[X_test.index[idx]]['mileage']
        
        print(f"     {model:20s} ({year:.0f}년, {mileage:6.0f}km): "
              f"실제 {actual:5.0f}만원 | 예측 {pred:5.0f}만원 | "
              f"오차 {error:4.0f}만원 ({error_pct:4.1f}%)")
    
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
    result = train_genesis_model()
    
    print("\n" + "="*70)
    print("  🎉 제네시스 모델 학습 완료!")
    print("="*70)
