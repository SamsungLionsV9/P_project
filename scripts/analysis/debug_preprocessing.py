import pandas as pd

print("Step 1: Load domestic data")
df_domestic = pd.read_csv('data/processed_encar_data.csv')
df_domestic.columns = df_domestic.columns.str.lower()
if 'car_type' not in df_domestic.columns:
    df_domestic['car_type'] = 'Domestic'
print(f"  Domestic: {len(df_domestic)}, car_type values: {df_domestic['car_type'].unique()}")

print("\nStep 2: Load imported data")
df_imported = pd.read_csv('encar_imported_data.csv')
print(f"  Original columns: {list(df_imported.columns)}")
df_imported.columns = df_imported.columns.str.lower()
print(f"  Lowercase columns: {list(df_imported.columns)}")
print(f"  Imported: {len(df_imported)}, cartype values: {df_imported['cartype'].unique()}")

print("\nStep 3: Rename columns")
imported_mapping = {
    'manufacturer': 'brand',
    'model': 'model_name',
    'fueltype': 'fuel',
    'cartype': 'car_type'
}
df_imported = df_imported.rename(columns=imported_mapping)
print(f"  After rename: {list(df_imported.columns)}")
print(f"  car_type values: {df_imported['car_type'].unique()}")

print("\nStep 4: Select columns")
required_cols = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price', 'car_type']
df_imported_selected = df_imported[required_cols]
print(f"  Selected: {len(df_imported_selected)}")
print(f"  car_type: {df_imported_selected['car_type'].unique()}")

print("\nStep 5: Merge")
df_combined = pd.concat([df_domestic[required_cols], df_imported_selected], ignore_index=True)
print(f"  Total: {len(df_combined)}")
print(f"  car_type counts:")
print(df_combined['car_type'].value_counts())

print("\nStep 6: Remove outliers")
df_combined['price'] = pd.to_numeric(df_combined['price'], errors='coerce')
df_combined['year'] = pd.to_numeric(df_combined['year'], errors='coerce')
df_combined['mileage'] = pd.to_numeric(df_combined['mileage'], errors='coerce')

print(f"  Before outlier removal:")
print(f"    Domestic: {len(df_combined[df_combined['car_type']=='Domestic'])}")
print(f"    Imported: {len(df_combined[df_combined['car_type']=='Imported'])}")

common_filter = (
    (df_combined['year'] >= 1990) & 
    (df_combined['year'] <= 2025) &
    (df_combined['mileage'] >= 0) & 
    (df_combined['mileage'] <= 500000) &
    (df_combined['price'] > 0)
)

domestic_filter = common_filter & (df_combined['car_type'] == 'Domestic') & (df_combined['price'] <= 50000)
imported_filter = common_filter & (df_combined['car_type'] == 'Imported') & (df_combined['price'] <= 100000)

print(f"\n  Domestic filter: {domestic_filter.sum()} rows")
print(f"  Imported filter: {imported_filter.sum()} rows")

df_result = df_combined[domestic_filter | imported_filter]
print(f"\n  After outlier removal:")
print(f"    Domestic: {len(df_result[df_result['car_type']=='Domestic'])}")
print(f"    Imported: {len(df_result[df_result['car_type']=='Imported'])}")
