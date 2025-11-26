"""추가 이상치 탐지 분석"""
import pandas as pd
import numpy as np

print("="*70)
print("🔍 추가 이상치 탐지 분석")
print("="*70)

df = pd.read_csv('encar_raw_domestic.csv')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 패턴 제거
patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]
df = df[df['Price'] > 100]

print(f"\n데이터: {len(df):,}행")

print("\n" + "="*70)
print("1️⃣ 연식 대비 주행거리 이상치")
print("="*70)
df['age'] = 2025 - df['YearOnly']
df['km_per_year'] = df['Mileage'] / (df['age'] + 1)

print(f"연간 주행거리 분포:")
print(f"  평균: {df['km_per_year'].mean():,.0f} km")
print(f"  중앙값: {df['km_per_year'].median():,.0f} km")
print(f"  5%: {df['km_per_year'].quantile(0.05):,.0f} km")
print(f"  95%: {df['km_per_year'].quantile(0.95):,.0f} km")

# 연간 주행거리가 비정상적인 경우
high_km = df[df['km_per_year'] > 50000]  # 연 5만km 이상
low_km = df[(df['km_per_year'] < 1000) & (df['age'] > 1)]  # 연 1000km 미만 (1년 이상)
print(f"\n연 5만km 초과 (과다주행): {len(high_km):,}건")
print(f"연 1000km 미만 (과소주행, 주행조작 의심): {len(low_km):,}건")

print("\n" + "="*70)
print("2️⃣ 가격 표준편차 기반 이상치 (2σ)")
print("="*70)
stats = df.groupby(['Model', 'YearOnly'])['Price'].agg(['mean', 'std', 'count']).reset_index()
stats = stats[stats['count'] >= 10]

df_merged = df.merge(stats, on=['Model', 'YearOnly'], how='left', suffixes=('', '_stat'))
df_merged['z_score'] = (df_merged['Price'] - df_merged['mean']) / df_merged['std'].replace(0, 1)
outliers_2sigma = df_merged[abs(df_merged['z_score']) > 2]
print(f"2σ 이상 이상치: {len(outliers_2sigma):,}건 ({len(outliers_2sigma)/len(df)*100:.1f}%)")

# 3σ 이상
outliers_3sigma = df_merged[abs(df_merged['z_score']) > 3]
print(f"3σ 이상 이상치: {len(outliers_3sigma):,}건 ({len(outliers_3sigma)/len(df)*100:.1f}%)")

print("\n" + "="*70)
print("3️⃣ 중복 데이터 확인")
print("="*70)
dups = df.duplicated(subset=['Model', 'Year', 'Mileage', 'Price'], keep=False)
print(f"완전 중복 데이터: {dups.sum():,}건 ({dups.sum()/len(df)*100:.1f}%)")

print("\n" + "="*70)
print("4️⃣ 싼타페 MX5 2023년 분석 (오차 높은 케이스)")
print("="*70)
santa = df[(df['Model'].str.contains('싼타페', na=False)) & (df['YearOnly']==2023)]
print(f"싼타페 2023년 (n={len(santa)})")
if len(santa) > 0:
    print(santa['Price'].describe())
    # 저가/고가 샘플
    print(f"\n저가 샘플:")
    print(santa.nsmallest(5, 'Price')[['Model', 'Year', 'Mileage', 'Price']])
    print(f"\n고가 샘플:")
    print(santa.nlargest(5, 'Price')[['Model', 'Year', 'Mileage', 'Price']])

print("\n" + "="*70)
print("💡 권장 이상치 제거 전략")
print("="*70)
print("1. 연간 주행거리 50,000km 초과 제거")
print("2. 연간 주행거리 1,000km 미만 (1년 이상 차량) 제거")
print("3. 모델+연식별 3σ 이상 가격 제거")
print("4. 중복 데이터 제거")
