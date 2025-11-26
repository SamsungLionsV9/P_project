import pandas as pd
import numpy as np

# 학습 시와 동일하게 데이터 준비
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

# 제네시스 제외
genesis_keywords = ['제네시스', 'GENESIS', 'Genesis']
genesis_mask = df['Manufacturer'].str.contains('|'.join(genesis_keywords), case=False, na=False)
df = df[~genesis_mask]

# 전처리
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])
df = df[df['Price'] > 100]
df = df[df['Price'] < 12000]
df['YearOnly'] = (df['Year']//100).astype(int)

# price_segment 계산
price_bins = pd.qcut(df['Price'], q=10, labels=False, duplicates='drop')
df['price_segment'] = price_bins

# 2022년식 그랜저의 price_segment 확인
granger_2022 = df[(df['Model'].str.contains('그랜저', na=False)) & (df['YearOnly']==2022)]
print("=== 2022년식 그랜저 price_segment 분포 ===")
print(granger_2022['price_segment'].value_counts().sort_index())
print(f"\n평균 price_segment: {granger_2022['price_segment'].mean():.2f}")
print(f"평균 가격: {granger_2022['Price'].mean():,.0f}만원")

# 전체 price_segment별 가격 범위
print("\n=== price_segment별 가격 범위 ===")
for seg in range(10):
    seg_data = df[df['price_segment']==seg]
    if len(seg_data) > 0:
        print(f"Segment {seg}: {seg_data['Price'].min():.0f} ~ {seg_data['Price'].max():.0f}만원 (평균 {seg_data['Price'].mean():.0f})")
