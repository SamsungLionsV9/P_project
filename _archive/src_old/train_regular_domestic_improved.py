"""
일반 국산차 모델 개선 버전
- 모델명 세대 파싱
- 트림 정보 활용
- 인기 모델 특화
- 주행거리/연식 세분화
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
import re

def extract_generation(model_name):
    """모델명에서 세대 정보 추출"""
    model_str = str(model_name)
    
    # 그랜저 세대
    if '그랜저' in model_str:
        if 'GN7' in model_str or '더 뉴 그랜저' in model_str:
            return 'GN7'
        elif 'IG' in model_str:
            return 'IG'
        elif 'HG' in model_str:
            return 'HG'
    
    # 쏘나타 세대
    elif '쏘나타' in model_str:
        if 'DN8' in model_str or '디 엣지' in model_str:
            return 'DN8'
        elif 'LF' in model_str:
            return 'LF'
        elif 'YF' in model_str:
            return 'YF'
    
    # 싼타페 세대
    elif '싼타페' in model_str:
        if 'MX5' in model_str or '5세대' in model_str:
            return 'MX5'
        elif 'TM' in model_str or '4세대' in model_str:
            return 'TM'
        elif 'DM' in model_str or '3세대' in model_str:
            return 'DM'
    
    # 투싼 세대
    elif '투싼' in model_str:
        if 'NX4' in model_str or '4세대' in model_str:
            return 'NX4'
        elif 'TL' in model_str or '3세대' in model_str:
            return 'TL'
    
    # K5 세대
    elif 'K5' in model_str:
        if 'DL3' in model_str or '3세대' in model_str:
            return 'DL3'
        elif 'JF' in model_str or '2세대' in model_str:
            return 'JF'
    
    # 쏘렌토 세대
    elif '쏘렌토' in model_str:
        if '4세대' in model_str or 'MQ4' in model_str:
            return 'MQ4'
        elif '3세대' in model_str or 'UM' in model_str:
            return 'UM'
    
    # 카니발 세대
    elif '카니발' in model_str:
        if '4세대' in model_str or 'KA4' in model_str:
            return 'KA4'
        elif '3세대' in model_str:
            return 'KA3'
    
    return 'unknown'

def extract_trim_features(model_name, fuel):
    """트림 특성 추출"""
    model_str = str(model_name).lower()
    
    features = {}
    
    # 하이브리드/전기 (연료와 교차 검증)
    features['is_hybrid'] = 1 if ('하이브리드' in model_str or '하이브리드' in fuel) else 0
    features['is_electric'] = 1 if ('전기' in model_str or '전기' in fuel) else 0
    
    # 고급 트림
    features['is_premium_trim'] = 1 if any(x in model_str for x in ['프레스티지', '시그니처', '노블레스', '익스클루시브']) else 0
    
    # N 라인 / 스포츠
    features['is_sport'] = 1 if any(x in model_str for x in ['n라인', 'n-라인', '스포츠']) else 0
    
    # 롱바디 / 7인승
    features['is_large'] = 1 if any(x in model_str for x in ['롱바디', '7인승', '9인승', '11인승']) else 0
    
    return features

def create_improved_features(df):
    """개선된 피처 엔지니어링"""
    print("  🔧 개선된 피처 생성 중...")
    
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # 기본 피처
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    
    # 연령 그룹 (더 세분화)
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 2, 3, 5, 7, 100], 
                              labels=['1년', '2년', '3년', '3-5년', '5-7년', '7년+'])
    
    # 주행거리 그룹
    df['mileage_group'] = pd.cut(df['mileage'],
                                  bins=[-1, 30000, 60000, 100000, 150000, 999999],
                                  labels=['3만이하', '3-6만', '6-10만', '10-15만', '15만+'])
    
    # 세대 정보 추출
    df['generation'] = df['model_name'].apply(extract_generation)
    
    # 트림 특성 추출
    trim_features = df.apply(lambda x: extract_trim_features(x['model_name'], x['fuel']), axis=1)
    for key in ['is_hybrid', 'is_electric', 'is_premium_trim', 'is_sport', 'is_large']:
        df[key] = trim_features.apply(lambda x: x[key])
    
    # 브랜드-연료 조합
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    
    # 모델 인기도
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    # 브랜드별 평균 가격
    brand_price_mean = df.groupby('brand')['price'].transform('mean')
    df['brand_avg_price'] = brand_price_mean
    
    # 모델별 평균 가격
    model_price_mean = df.groupby('model_name')['price'].transform('mean')
    df['model_avg_price'] = model_price_mean
    
    # 가격 vs 모델 평균
    df['price_vs_model_avg'] = df['price'] / (model_price_mean + 1)
    
    # 연식-주행거리 상호작용
    df['age_mileage_interaction'] = df['age'] * np.log1p(df['mileage'])
    
    # 주행거리 과다 여부 (연간 2만km 기준)
    df['is_overmileage'] = (df['mileage_per_year'] > 20000).astype(int)
    
    # 인기 모델 표시
    popular_models = ['그랜저', '아반떼', '쏘나타', 'K5', '싼타페', '투싼', '쏘렌토', '카니발', '스포티지', '코나']
    df['is_popular_model'] = df['model_name'].apply(
        lambda x: 1 if any(m in str(x) for m in popular_models) else 0
    )
    
    # SUV/세단/MPV 구분
    df['vehicle_type'] = 'sedan'
    suv_keywords = ['싼타페', '투싼', '쏘렌토', '스포티지', '셀토스', '코나', '팰리세이드', '모하비']
    mpv_keywords = ['카니발', '스타렉스', '스타리아']
    
    for keyword in suv_keywords:
        df.loc[df['model_name'].str.contains(keyword, na=False), 'vehicle_type'] = 'suv'
    for keyword in mpv_keywords:
        df.loc[df['model_name'].str.contains(keyword, na=False), 'vehicle_type'] = 'mpv'
    
    # 로그 변환
    df['log_price'] = np.log1p(df['price'])
    
    print(f"     ✓ 생성된 피처 수: {len([c for c in df.columns if c not in ['price', 'log_price']])}")
    
    return df

def train_improved_model(data_path='../data/processed_encar_combined.csv',
                        model_path='../models/regular_domestic_improved.pkl'):
    """개선된 일반 국산차 모델 학습"""
    
    print("\n" + "="*70)
    print("  🚗 일반 국산차 모델 학습 (개선 버전)")
    print("="*70)
    
    # 데이터 로드
    print("\n  📂 데이터 로딩...")
    df = pd.read_csv(data_path)
    
    # 국산차 중 제네시스 제외
    df = df[(df['car_type'] == 'Domestic') & (df['brand'] != '제네시스')].copy()
    print(f"     일반 국산차 데이터: {len(df):,}건")
    
    # 피처 엔지니어링
    df = create_improved_features(df)
    
    # 이상치 제거 (더 보수적으로)
    initial_count = len(df)
    
    # 1. 극단적 가격
    df = df[(df['price'] >= 100) & (df['price'] <= 8000)]
    
    # 2. 극단적 주행거리 (연간 5만km 이상은 이상)
    df = df[df['mileage_per_year'] <= 50000]
    
    # 3. 너무 오래된 차량 (15년 이상)
    df = df[df['age'] <= 15]
    
    removed = initial_count - len(df)
    print(f"  🧹 이상치 제거: {removed:,}건")
    print(f"  최종 데이터: {len(df):,}건")
    print(f"  가격 범위: {df['price'].min():.0f}만원 ~ {df['price'].max():.0f}만원")
    
    # 피처 선택
    categorical_features = [
        'brand', 'model_name', 'fuel', 
        'age_group', 'mileage_group', 'generation',
        'brand_fuel', 'vehicle_type'
    ]
    
    numerical_features = [
        'age', 'mileage', 'mileage_per_year',
        'is_low_mileage', 'is_high_mileage', 'is_overmileage',
        'model_popularity_log', 'brand_avg_price', 'model_avg_price',
        'age_mileage_interaction',
        'is_hybrid', 'is_electric', 'is_premium_trim', 'is_sport', 'is_large',
        'is_popular_model'
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
    
    # 개선된 하이퍼파라미터
    xgb_params = {
        'n_estimators': 1500,        # 더 많은 트리
        'learning_rate': 0.03,       # 더 천천히 학습
        'max_depth': 8,              # 더 깊은 트리
        'min_child_weight': 5,       # 과적합 방지
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.5,
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
    
    # 가격대별 성능
    print(f"\n  💰 가격대별 예측 정확도:")
    
    price_ranges = [
        (0, 1000, "저가 (<1000만원)"),
        (1000, 2000, "중저가 (1000-2000만원)"),
        (2000, 3000, "중가 (2000-3000만원)"),
        (3000, 5000, "고가 (3000-5000만원)"),
        (5000, 10000, "초고가 (5000만원+)")
    ]
    
    for min_p, max_p, label in price_ranges:
        mask = (y_test_actual >= min_p) & (y_test_actual < max_p)
        if mask.sum() == 0:
            continue
        
        subset_mae = mean_absolute_error(y_test_actual[mask], y_test_pred_actual[mask])
        subset_mape = np.mean(np.abs((y_test_actual[mask] - y_test_pred_actual[mask]) / y_test_actual[mask])) * 100
        print(f"     {label:25s}: MAE {subset_mae:5.0f}만원, MAPE {subset_mape:5.1f}%, N={mask.sum():,}")
    
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
    result = train_improved_model()
    
    print("\n" + "="*70)
    print("  🎉 개선된 일반 국산차 모델 학습 완료!")
    print("="*70)
    
    print(f"\n📊 최종 성능:")
    print(f"   Test R²: {result['test_r2']:.4f}")
    print(f"   Test MAE: {result['test_mae']:.0f}만원")
    print(f"   Test MAPE: {result['test_mape']:.2f}%")
    print(f"   CV R²: {result['cv_r2']:.4f}")
