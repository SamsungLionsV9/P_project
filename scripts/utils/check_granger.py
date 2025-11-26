import pandas as pd
import numpy as np

# 원본 데이터 확인
df = pd.read_csv('encar_raw_domestic.csv')
df['YearOnly'] = (df['Year']//100).astype(int)

# 2022년식 그랜저, 주행거리 30000~40000
granger = df[(df['Model'].str.contains('그랜저', na=False)) & 
             (df['YearOnly']==2022) & 
             (df['Mileage'] >= 30000) & 
             (df['Mileage'] <= 40000)]

print(f"2022년식 그랜저 (30k~40k km): {len(granger)}대")
print(f"평균 가격: {granger['Price'].mean():,.0f}만원")
print(f"중앙값: {granger['Price'].median():,.0f}만원")
print(f"가격 범위: {granger['Price'].min():.0f} ~ {granger['Price'].max():.0f}만원")
print(f"log 평균: {np.log1p(granger['Price']).mean():.4f}")

# Price 컬럼 확인
print(f"\n전체 데이터 Price 범위: {df['Price'].min()} ~ {df['Price'].max()}")
print(f"Price 타입: {df['Price'].dtype}")
print(f"Price 샘플: {df['Price'].head(10).tolist()}")
