"""너무 낮은 가격 이상치 분석"""
import pandas as pd
import numpy as np

print("="*70)
print("🔍 너무 낮은 가격 이상치 분석")
print("="*70)

# 국산차 데이터
df = pd.read_csv('encar_raw_domestic.csv')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df['YearOnly'] = (df['Year'] // 100).astype(int)
df = df[df['YearOnly'] >= 2015]  # 최근 10년

print(f"데이터: {len(df):,}행")

# 모델+연식별 통계
stats = df.groupby(['Model', 'YearOnly'])['Price'].agg(['min', 'mean', 'median', 'max', 'count',
                                                         lambda x: x.quantile(0.05),
                                                         lambda x: x.quantile(0.95)])
stats.columns = ['min', 'mean', 'median', 'max', 'count', 'Q05', 'Q95']
stats = stats.reset_index()
stats = stats[stats['count'] >= 10]  # 최소 10개 이상

# 최소값이 Q05의 50% 미만인 경우 = 이상치 있음
stats['low_ratio'] = stats['min'] / stats['Q05']
suspicious = stats[stats['low_ratio'] < 0.5].sort_values('low_ratio')

print(f"\n📊 너무 낮은 이상치 의심 모델 (min < Q05 * 0.5):")
print("-"*70)
for _, row in suspicious.head(20).iterrows():
    print(f"{row['Model']} {row['YearOnly']}년: min={row['min']:,.0f} / Q05={row['Q05']:,.0f} / median={row['median']:,.0f} (비율={row['low_ratio']:.2f}x)")

# 실제 이상치 샘플
print(f"\n📋 너무 낮은 가격 샘플:")
print("-"*70)
for _, row in suspicious.head(3).iterrows():
    model, year, q05, median = row['Model'], row['YearOnly'], row['Q05'], row['median']
    low_outliers = df[(df['Model']==model) & (df['YearOnly']==year) & (df['Price'] < q05 * 0.5)]
    if len(low_outliers) > 0:
        print(f"\n{model} {year}년 (Q05={q05:,.0f}, 중앙값={median:,.0f}):")
        print(low_outliers[['Manufacturer', 'Model', 'Year', 'Mileage', 'Price']].head(5).to_string())

# 연식 대비 가격 비율 분석
print(f"\n" + "="*70)
print("💡 연식별 최소 합리적 가격 분석")
print("="*70)

# 연식별 평균 가격 (신차 가격 추정)
year_price = df.groupby('YearOnly')['Price'].agg(['mean', 'median', 'min']).reset_index()
print("\n연식별 가격 분포:")
for _, row in year_price.iterrows():
    min_ratio = row['min'] / row['median'] * 100
    print(f"{row['YearOnly']}년: 중앙값 {row['median']:,.0f}만원, 최소 {row['min']:,.0f}만원 ({min_ratio:.0f}%)")

# 수입차도 확인
print(f"\n" + "="*70)
print("📊 수입차 낮은 가격 분석")
print("="*70)

df_i = pd.read_csv('encar_imported_data.csv')
df_i = df_i.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df_i['YearOnly'] = (df_i['Year'] // 100).astype(int)
df_i = df_i[df_i['YearOnly'] >= 2015]

# 비정상적으로 낮은 가격
low_prices = df_i[df_i['Price'] < 500]  # 500만원 미만
print(f"500만원 미만 수입차: {len(low_prices):,}건")
if len(low_prices) > 0:
    print(low_prices[['Manufacturer', 'Model', 'Year', 'Mileage', 'Price']].head(10).to_string())
