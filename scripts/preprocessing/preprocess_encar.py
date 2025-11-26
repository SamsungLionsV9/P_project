import pandas as pd
import numpy as np

def preprocess_encar_data(input_file='encar_raw_data_final.csv', output_file='processed_encar_data.csv'):
    import os
    
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Checking for processed_encar_data.csv...")
        if os.path.exists('processed_encar_data.csv'):
            print("Found processed_encar_data.csv. Using it as input for cleaning.")
            df = pd.read_csv('processed_encar_data.csv')
            # Columns are already renamed and features created
            # Just ensure we have the right columns
            required_cols = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price']
            if all(col in df.columns for col in required_cols):
                df_processed = df[required_cols].copy()
                # Skip to cleaning
                pass
            else:
                print("Error: processed_encar_data.csv missing required columns.")
                return
        else:
            print("Error: No data file found.")
            return
    else:
        print("Loading raw data...")
        df = pd.read_csv(input_file)
        
        print(f"Raw data shape: {df.shape}")
        
        # 1. Rename columns to match our convention
        df = df.rename(columns={
            'Manufacturer': 'brand',
            'Mileage': 'mileage',
            'FuelType': 'fuel',
            'Price': 'price'
        })
        
        # 2. Process Year
        df['year'] = df['Year'].astype(str).str[:4].astype(int)
        
        # 3. Create a 'model_name' feature
        df['model_name'] = df['Model']
        
        # 4. Select features for training
        features = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price']
        df_processed = df[features].copy()
    
    # 5. Data Cleaning
    print("Cleaning data...")
    
    # 5.1 Filter invalid prices
    initial_count = len(df_processed)
    df_processed = df_processed[df_processed['price'] > 0]
    print(f"Dropped {initial_count - len(df_processed)} rows with price <= 0")
    
    # 5.2 Normalize Price Units
    # Assumption: Prices < 100 are likely in Million Won (e.g. 47.0), need to be converted to Man-won (4700).
    # Prices >= 100 are likely already in Man-won.
    mask_million = df_processed['price'] < 100
    print(f"Converting {mask_million.sum()} rows from Million Won to Man-won")
    df_processed.loc[mask_million, 'price'] = df_processed.loc[mask_million, 'price'] * 100
    
    # 5.3 Drop any remaining nulls
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
