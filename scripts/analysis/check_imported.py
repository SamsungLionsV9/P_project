import pandas as pd

df = pd.read_csv('encar_imported_data.csv')
print(f'Total: {len(df)}')
print(f'Columns: {list(df.columns)}')
print(f'\nCarType values:')
print(df['CarType'].value_counts())
print(f'\nPrice stats:')
print(f'  Min: {df["Price"].min()}')
print(f'  Max: {df["Price"].max()}')
print(f'  Mean: {df["Price"].mean():.0f}')
print(f'\nFirst 5 rows:')
print(df.head())
