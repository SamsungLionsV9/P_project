import pandas as pd
import numpy as np
import joblib
import sys

def create_features(df):
    """Feature engineering (same as training)"""
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # Mileage features
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    
    # Age groups
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    # Brand-fuel interaction
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    
    # Model popularity
    # Note: For single prediction, we use a default value
    df['model_popularity_log'] = 5.0  # Average popularity
    
    # Premium brand
    premium_brands = ['제네시스', '벤츠', 'BMW', '아우디', '렉서스', '포르쉐']
    df['is_premium'] = df['brand'].isin(premium_brands).astype(int)
    
    # Premium interactions
    df['premium_age'] = df['is_premium'] * df['age']
    df['premium_mileage'] = df['is_premium'] * df['mileage']
    
    # Brand mileage (use default for single prediction)
    df['mileage_vs_brand_avg'] = 1.0
    
    # Eco-friendly
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    return df

def predict_price(brand, model_name, year, mileage, fuel, model_path='improved_car_price_model.pkl'):
    try:
        # Load model
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"Error: Model file '{model_path}' not found. Please run train_model_improved.py first.")
        return

    # Prepare input data
    input_data = pd.DataFrame({
        'brand': [brand],
        'model_name': [model_name],
        'year': [year],
        'mileage': [mileage],
        'fuel': [fuel]
    })
    
    # Apply feature engineering
    input_data = create_features(input_data)
    
    # Select features (must match training)
    feature_cols = [
        'brand', 'model_name', 'fuel', 'age', 'mileage',
        'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
        'age_group', 'brand_fuel', 'model_popularity_log',
        'is_premium', 'premium_age', 'premium_mileage',
        'mileage_vs_brand_avg', 'is_eco'
    ]
    
    X = input_data[feature_cols]
    
    print("\n입력 정보:")
    print(f"  브랜드: {brand}")
    print(f"  모델: {model_name}")
    print(f"  연식: {year}년")
    print(f"  주행거리: {mileage:,}km")
    print(f"  연료: {fuel}")
    print(f"  차량 나이: {input_data['age'].values[0]}년")
    print(f"  프리미엄 브랜드: {'예' if input_data['is_premium'].values[0] else '아니오'}")
    
    # Predict
    try:
        log_pred = model.predict(X)[0]
        pred_price = np.expm1(log_pred)
        
        print(f"\n💰 예상 가격: {pred_price:,.0f}만원")
        print(f"   (약 {pred_price*10000:,.0f}원)")
        
        # Price range
        margin = pred_price * 0.10  # ±10% margin
        print(f"\n가격 범위 (±10%): {pred_price-margin:,.0f} ~ {pred_price+margin:,.0f}만원")
        
        return pred_price
    except Exception as e:
        print(f"예측 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    print("=== Used Car Price Predictor ===")
    
    if len(sys.argv) > 1:
        # Command line usage
        # python predict_car_price.py "현대" "그랜저 IG" 2018 50000 "가솔린"
        if len(sys.argv) != 6:
            print("Usage: python predict_car_price.py [Brand] [Model] [Year] [Mileage] [Fuel]")
            print('Example: python predict_car_price.py "현대" "그랜저 IG" 2018 50000 "가솔린"')
        else:
            predict_price(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        # Interactive mode
        print("Enter car details to get a prediction.")
        brand = input("Brand (e.g., 현대, 기아): ")
        model_name = input("Model Name (e.g., 그랜저 IG, 아반떼 (CN7)): ")
        year = int(input("Year (YYYY): "))
        mileage = int(input("Mileage (km): "))
        fuel = input("Fuel (e.g., 가솔린, 디젤): ")
        
        predict_price(brand, model_name, year, mileage, fuel)
