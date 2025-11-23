import pandas as pd
import numpy as np
import joblib
import sys

def predict_price(brand, model_name, year, mileage, fuel, model_path='best_car_price_model.pkl'):
    try:
        # Load model
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"Error: Model file '{model_path}' not found. Please run train_model_advanced.py first.")
        return

    # Prepare input data
    # We need to match the features used in training: ['brand', 'model_name', 'age', 'mileage', 'fuel']
    current_year = 2025
    age = current_year - year
    
    input_data = pd.DataFrame({
        'brand': [brand],
        'model_name': [model_name],
        'age': [age],
        'mileage': [mileage],
        'fuel': [fuel]
    })
    
    print("\nInput Data:")
    print(input_data)
    
    # Predict
    # The model predicts log(price), so we need to apply expm1
    try:
        log_pred = model.predict(input_data)[0]
        pred_price = np.expm1(log_pred)
        
        print(f"\n💰 Predicted Price: {pred_price:,.0f} Man-won")
        print(f"(Approx. {pred_price*10000:,.0f} KRW)")
        
        return pred_price
    except Exception as e:
        print(f"Error during prediction: {e}")
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
