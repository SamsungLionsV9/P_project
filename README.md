# Used Car Price Predictor (Encar) 🚗💰

This project collects used car data from **Encar**, trains an **XGBoost** machine learning model, and predicts the market price of domestic cars in Korea.

## 📂 Project Structure

- **`scrape_encar_partitioned.py`**: The robust scraper that collects ~120,000 car records from Encar API using price partitioning to bypass limits.
- **`preprocess_encar.py`**: Cleans the raw data, handles feature engineering (Car Age, Log Price), and prepares it for training.
- **`train_model_advanced.py`**: Trains an XGBoost model with **RandomizedSearchCV** for hyperparameter tuning and **Log-transformation** for better accuracy.
- **`predict_car_price.py`**: Inference script to predict the price of a specific car.
- **`best_car_price_model.pkl`**: The trained and optimized model file.
- **`processed_encar_data.csv`**: The cleaned dataset used for training (119,368 records).

## 🚀 How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Collect Data (Optional)
If you want to collect fresh data:
```bash
python scrape_encar_partitioned.py
```
*Note: This takes about 10-15 minutes.*

### 3. Preprocess Data
```bash
python preprocess_encar.py
```

### 4. Train Model
```bash
python train_model_advanced.py
```
*Output: `best_car_price_model.pkl` and performance metrics.*

### 5. Predict Price
Run the prediction script with car details:
```bash
# Usage: python predict_car_price.py [Brand] [Model] [Year] [Mileage] [Fuel]
python predict_car_price.py "현대" "그랜저 IG" 2020 40000 "가솔린"
```

## 📊 Model Performance

- **MAE (Mean Absolute Error)**: ~384 Man-won (approx. 3.84 million KRW)
- **R2 Score**: 0.53
- **Data Coverage**: 119,368 unique domestic cars (Full Market Coverage)

## 📝 Notes
- The model uses `log1p` transformation for the target variable to handle the wide range of car prices effectively.
- Feature `age` is calculated as `2025 - year`.
