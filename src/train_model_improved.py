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

# Set plot style
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def create_features(df):
    """Enhanced feature engineering"""
    print("Creating enhanced features...")
    
    current_year = 2025
    df['age'] = current_year - df['year']
    
    # 1. Mileage-based features
    df['mileage_per_year'] = df['mileage'] / (df['age'] + 1)
    df['is_low_mileage'] = (df['mileage'] < 30000).astype(int)
    df['is_high_mileage'] = (df['mileage'] > 150000).astype(int)
    
    # 2. Age groups
    df['age_group'] = pd.cut(df['age'], 
                              bins=[-1, 1, 3, 5, 10, 100], 
                              labels=['new', 'semi_new', 'used', 'old', 'very_old'])
    
    # 3. Brand-fuel interaction
    df['brand_fuel'] = df['brand'] + '_' + df['fuel']
    
    # 4. Model popularity (frequency encoding)
    model_counts = df['model_name'].value_counts()
    df['model_popularity'] = df['model_name'].map(model_counts)
    df['model_popularity_log'] = np.log1p(df['model_popularity'])
    
    # 5. Premium brand indicator
    premium_brands = ['제네시스', '벤츠', 'BMW', '아우디', '렉서스', '포르쉐', 
                      '페라리', '람보르기니', '벤틀리', '롤스로이스']
    df['is_premium'] = df['brand'].isin(premium_brands).astype(int)
    
    # 6. Premium interaction features
    df['premium_age'] = df['is_premium'] * df['age']
    df['premium_mileage'] = df['is_premium'] * df['mileage']
    
    # 7. Brand-specific mileage normalization
    brand_mileage_mean = df.groupby('brand')['mileage'].transform('mean')
    df['mileage_vs_brand_avg'] = df['mileage'] / (brand_mileage_mean + 1)
    
    # 8. Electric/Hybrid indicator
    df['is_eco'] = df['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
    
    print(f"Created {len([c for c in df.columns if c not in ['price', 'log_price', 'year']])} features")
    
    return df

def train_improved_model(data_path='processed_encar_data.csv', 
                         model_path='improved_car_price_model.pkl'):
    print("=" * 60)
    print("IMPROVED CAR PRICE PREDICTION MODEL")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data...")
    df = pd.read_csv(data_path)
    print(f"Original shape: {df.shape}")
    
    # Remove outliers
    print("\n2. Cleaning outliers...")
    print(f"Prices > 9000: {len(df[df['price'] > 9000])}")
    print(f"Prices == 9999: {len(df[df['price'] == 9999])}")
    
    # Remove placeholder values and extreme outliers
    df = df[(df['price'] <= 9000) & (df['price'] != 9999)].copy()
    print(f"After cleaning: {df.shape}")
    
    # Feature engineering
    df = create_features(df)
    
    # Log transform target
    df['log_price'] = np.log1p(df['price'])
    
    # Select features
    feature_cols = [
        # Original features
        'brand', 'model_name', 'fuel', 'age', 'mileage',
        # New features
        'mileage_per_year', 'is_low_mileage', 'is_high_mileage',
        'age_group', 'brand_fuel', 'model_popularity_log',
        'is_premium', 'premium_age', 'premium_mileage',
        'mileage_vs_brand_avg', 'is_eco'
    ]
    
    X = df[feature_cols]
    y = df['log_price']
    
    print(f"\n3. Feature summary:")
    print(f"Total features: {len(feature_cols)}")
    print(f"Categorical: {len([c for c in feature_cols if c in ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel']])}")
    print(f"Numerical: {len([c for c in feature_cols if c not in ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel']])}")
    
    # Train-test split with stratification
    print("\n4. Splitting data...")
    # Create price bins for stratification
    price_bins = pd.qcut(df['price'], q=5, labels=False, duplicates='drop')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=price_bins
    )
    print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    
    # Preprocessing pipeline
    print("\n5. Building preprocessing pipeline...")
    categorical_features = ['brand', 'model_name', 'fuel', 'age_group', 'brand_fuel']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             categorical_features)
        ],
        remainder='passthrough'
    )
    
    # Model with sample weights for high-price cars
    print("\n6. Training XGBoost with enhanced parameters...")
    
    # Calculate sample weights (higher weight for expensive cars)
    y_train_actual = np.expm1(y_train)
    sample_weights = np.where(y_train_actual > 5000, 2.0, 1.0)
    sample_weights = np.where(y_train_actual < 1000, 1.2, sample_weights)
    
    xgb = XGBRegressor(
        random_state=42, 
        n_jobs=-1,
        tree_method='hist'
    )
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', xgb)
    ])
    
    # Enhanced hyperparameter grid
    param_grid = {
        'regressor__n_estimators': [1000, 1500, 2000],
        'regressor__learning_rate': [0.01, 0.05, 0.1],
        'regressor__max_depth': [4, 5, 6, 7],
        'regressor__min_child_weight': [1, 3, 5],
        'regressor__subsample': [0.7, 0.8, 0.9],
        'regressor__colsample_bytree': [0.7, 0.8, 0.9],
        'regressor__gamma': [0, 0.1, 0.2],
        'regressor__reg_alpha': [0, 0.01, 0.1],
        'regressor__reg_lambda': [0.5, 1, 1.5]
    }
    
    search = RandomizedSearchCV(
        pipeline, 
        param_distributions=param_grid, 
        n_iter=20,  # Increased iterations
        cv=3, 
        scoring='neg_mean_absolute_error', 
        verbose=2, 
        n_jobs=-1,
        random_state=42
    )
    
    search.fit(X_train, y_train, regressor__sample_weight=sample_weights)
    
    best_model = search.best_estimator_
    print(f"\nBest Params: {search.best_params_}")
    
    # Evaluation
    print("\n7. Evaluating model...")
    y_pred_log = best_model.predict(X_test)
    
    y_test_actual = np.expm1(y_test)
    y_pred_actual = np.expm1(y_pred_log)
    
    rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
    mae = mean_absolute_error(y_test_actual, y_pred_actual)
    r2 = r2_score(y_test_actual, y_pred_actual)
    
    # MAPE
    mape = np.mean(np.abs((y_test_actual - y_pred_actual) / y_test_actual)) * 100
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"RMSE: {rmse:.2f} 만원")
    print(f"MAE: {mae:.2f} 만원")
    print(f"R² Score: {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    
    # Price range performance
    print(f"\n{'='*60}")
    print("PERFORMANCE BY PRICE RANGE")
    print(f"{'='*60}")
    
    test_df = pd.DataFrame({
        'actual': y_test_actual,
        'predicted': y_pred_actual
    })
    
    price_ranges = [
        (0, 1000, "저가 (<1000)"),
        (1000, 2000, "중저가 (1000-2000)"),
        (2000, 4000, "중가 (2000-4000)"),
        (4000, 10000, "고가 (4000+)")
    ]
    
    for low, high, label in price_ranges:
        mask = (test_df['actual'] >= low) & (test_df['actual'] < high)
        subset = test_df[mask]
        if len(subset) > 0:
            subset_mae = mean_absolute_error(subset['actual'], subset['predicted'])
            subset_mape = np.mean(np.abs((subset['actual'] - subset['predicted']) / subset['actual'])) * 100
            subset_r2 = r2_score(subset['actual'], subset['predicted'])
            print(f"{label:20s}: MAE={subset_mae:6.0f}만원, MAPE={subset_mape:5.1f}%, R²={subset_r2:.3f}, N={len(subset):5d}")
    
    # Visualization
    print(f"\n8. Creating visualizations...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Scatter plot
    axes[0].scatter(y_test_actual, y_pred_actual, alpha=0.4, s=10)
    min_val = min(y_test_actual.min(), y_pred_actual.min())
    max_val = max(y_test_actual.max(), y_pred_actual.max())
    axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    axes[0].set_xlabel('Actual Price (만원)', fontsize=12)
    axes[0].set_ylabel('Predicted Price (만원)', fontsize=12)
    axes[0].set_title(f'Improved Model: R²={r2:.3f}, MAPE={mape:.1f}%', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Residual plot
    residuals = y_test_actual - y_pred_actual
    axes[1].scatter(y_test_actual, residuals, alpha=0.4, s=10)
    axes[1].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Actual Price (만원)', fontsize=12)
    axes[1].set_ylabel('Residual (만원)', fontsize=12)
    axes[1].set_title('Residual Plot', fontsize=14)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('improved_prediction_plot.png', dpi=100)
    print("✓ Saved improved_prediction_plot.png")
    
    # Save model
    joblib.dump(best_model, model_path)
    print(f"✓ Saved model to {model_path}")
    
    # Save metrics
    with open('improved_metrics.txt', 'w', encoding='utf-8') as f:
        f.write(f"=== Improved Model Metrics ===\n")
        f.write(f"RMSE: {rmse:.2f} 만원\n")
        f.write(f"MAE: {mae:.2f} 만원\n")
        f.write(f"R²: {r2:.4f}\n")
        f.write(f"MAPE: {mape:.2f}%\n\n")
        f.write(f"Best Params:\n{search.best_params_}\n\n")
        f.write(f"Price Range Performance:\n")
        for low, high, label in price_ranges:
            mask = (test_df['actual'] >= low) & (test_df['actual'] < high)
            subset = test_df[mask]
            if len(subset) > 0:
                subset_mae = mean_absolute_error(subset['actual'], subset['predicted'])
                subset_mape = np.mean(np.abs((subset['actual'] - subset['predicted']) / subset['actual'])) * 100
                f.write(f"{label}: MAE={subset_mae:.0f}, MAPE={subset_mape:.1f}%, N={len(subset)}\n")
    
    print("✓ Saved improved_metrics.txt")
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    train_improved_model()
