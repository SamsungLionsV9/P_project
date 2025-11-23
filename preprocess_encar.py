import pandas as pd
import numpy as np

def preprocess_encar_data(input_file='encar_raw_data_final.csv', output_file='processed_encar_data.csv'):
    print("Loading data...")
    df = pd.read_csv(input_file)
    
    print(f"Raw data shape: {df.shape}")
    
    # 1. Rename columns to match our convention
    # Manufacturer -> brand
    # Year -> year (needs processing)
    # Mileage -> mileage
    # FuelType -> fuel
    # Price -> price
    
    df = df.rename(columns={
        'Manufacturer': 'brand',
        'Mileage': 'mileage',
        'FuelType': 'fuel',
        'Price': 'price'
    })
    
    # 2. Process Year
    # Encar Year is likely YYYYMM (float), e.g., 201407.0
    # We want just YYYY
    df['year'] = df['Year'].astype(str).str[:4].astype(int)
    
    # 3. Create a 'model_name' feature
    df['model_name'] = df['Model']
    
    # 4. Select features for training
    features = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price']
    df_processed = df[features].copy()
    
    # 5. Drop any remaining nulls (should be none based on info, but safe to check)
    df_processed = df_processed.dropna()
    
    print(f"Processed data shape: {df_processed.shape}")
    
    # Save
    df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Saved processed data to {output_file}")
    
    # Stats
    print("\nData Statistics:")
    print(df_processed.describe())
    
    return df_processed

if __name__ == "__main__":
    preprocess_encar_data()
