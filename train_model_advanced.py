import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

# Set plot style
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic' # For Korean support
plt.rcParams['axes.unicode_minus'] = False

def train_advanced_model(data_path='processed_encar_data.csv', model_path='best_car_price_model.pkl'):
    print("Loading data...")
    df = pd.read_csv(data_path)
    
    # 1. Feature Engineering
    print("Feature Engineering...")
    # Car Age
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # Log transform Price (Target) to handle skewness
    # We will train on log(price) and exponentiate predictions later
    df['log_price'] = np.log1p(df['price'])
    
    features = ['brand', 'model_name', 'age', 'mileage', 'fuel']
    target = 'log_price'
    
    X = df[features]
    y = df[target]
    
    print(f"Data Shape: {X.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. Preprocessing
    categorical_features = ['brand', 'model_name', 'fuel']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ],
        remainder='passthrough'
    )
    
    # 3. Model & Tuning
    xgb = XGBRegressor(random_state=42, n_jobs=-1)
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', xgb)
    ])
    
    # Hyperparameter Grid
    param_grid = {
        'regressor__n_estimators': [500, 1000, 1500],
        'regressor__learning_rate': [0.01, 0.05, 0.1],
        'regressor__max_depth': [3, 5, 7, 9],
        'regressor__subsample': [0.7, 0.8, 0.9],
        'regressor__colsample_bytree': [0.7, 0.8, 0.9]
    }
    
    print("Starting Hyperparameter Tuning (RandomizedSearchCV)...")
    # Use RandomizedSearch to find good params efficiently
    search = RandomizedSearchCV(
        pipeline, 
        param_distributions=param_grid, 
        n_iter=10, # Try 10 combinations
        cv=3, 
        scoring='neg_mean_absolute_error', 
        verbose=1, 
        n_jobs=-1,
        random_state=42
    )
    
    search.fit(X_train, y_train)
    
    best_model = search.best_estimator_
    print(f"Best Params: {search.best_params_}")
    
    # 4. Evaluation
    print("Evaluating best model...")
    y_pred_log = best_model.predict(X_test)
    
    # Inverse transform to get actual prices
    y_test_actual = np.expm1(y_test)
    y_pred_actual = np.expm1(y_pred_log)
    
    rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
    mae = mean_absolute_error(y_test_actual, y_pred_actual)
    r2 = r2_score(y_test_actual, y_pred_actual)
    
    print(f"\n=== Final Results ===")
    print(f"RMSE: {rmse:.2f} Man-won")
    print(f"MAE: {mae:.2f} Man-won")
    print(f"R2 Score: {r2:.4f}")
    
    # 5. Visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_test_actual, y=y_pred_actual, alpha=0.5)
    plt.plot([0, max(y_test_actual)], [0, max(y_test_actual)], 'r--')
    plt.xlabel('Actual Price')
    plt.ylabel('Predicted Price')
    plt.title(f'Actual vs Predicted Price (R2={r2:.2f})')
    plt.savefig('prediction_plot.png')
    print("Saved prediction_plot.png")
    
    # Save model
    joblib.dump(best_model, model_path)
    print(f"Saved best model to {model_path}")
    
    # Save metrics
    with open('advanced_metrics.txt', 'w') as f:
        f.write(f"RMSE: {rmse:.2f}\n")
        f.write(f"MAE: {mae:.2f}\n")
        f.write(f"R2: {r2:.4f}\n")
        f.write(f"Best Params: {search.best_params_}\n")

if __name__ == "__main__":
    train_advanced_model()
