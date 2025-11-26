import pandas as pd
import requests

df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)
patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]
df = df[df['YearOnly'] >= 2018]
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')

spark = df[(df['Model'].str.contains('스파크', na=False)) & (df['YearOnly']==2020)]
print(f"스파크 2020 데이터: {len(spark)}개")

# 중앙값 샘플
median_idx = spark['Price'].sub(spark['Price'].median()).abs().idxmin()
sample = spark.loc[median_idx]
print(f"\n테스트 샘플:")
print(f"  Model: {sample['Model']}")
print(f"  Manufacturer: {sample['Manufacturer']}")
print(f"  Year: {sample['Year']}")
print(f"  YearOnly: {sample['YearOnly']}")
print(f"  Mileage: {sample['Mileage']}")
print(f"  Price: {sample['Price']}")

# API 테스트
resp = requests.post('http://localhost:8000/api/predict', json={
    'brand': sample['Manufacturer'],
    'model': sample['Model'],
    'year': int(sample['YearOnly']),
    'mileage': int(sample['Mileage']),
    'fuel': '가솔린'
})
print(f"\nAPI 예측: {resp.json()['predicted_price']:.0f}만원")
print(f"오차: {abs(resp.json()['predicted_price'] - sample['Price']) / sample['Price'] * 100:.1f}%")
