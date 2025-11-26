"""모델+연식별 최대가격 분석 및 이상치 탐지"""
import pandas as pd
import numpy as np

print("="*70)
print("🔍 모델+연식별 최대가격 기반 이상치 분석")
print("="*70)

# 데이터 로드
df = pd.read_csv('encar_imported_data.csv')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model'])
df['YearOnly'] = (df['Year'] // 100).astype(int)

print(f"원본 데이터: {len(df):,}행")

# 모델+연식별 통계
stats = df.groupby(['Model', 'YearOnly'])['Price'].agg(['mean', 'median', 'max', 'std', 'count', 
                                                         lambda x: x.quantile(0.95),
                                                         lambda x: x.quantile(0.99)])
stats.columns = ['mean', 'median', 'max', 'std', 'count', 'Q95', 'Q99']
stats = stats.reset_index()

# 최대값이 Q95의 2배 이상인 경우 = 이상치 있음
stats['outlier_ratio'] = stats['max'] / stats['Q95']
suspicious = stats[stats['outlier_ratio'] > 2].sort_values('outlier_ratio', ascending=False)

print(f"\n📊 이상치 의심 모델 (max > Q95 * 2):")
print("-"*70)
for _, row in suspicious.head(20).iterrows():
    print(f"{row['Model']} {row['YearOnly']}년: max={row['max']:,.0f} / Q95={row['Q95']:,.0f} / 비율={row['outlier_ratio']:.1f}x")

# 실제 이상치 샘플 확인
print(f"\n📋 이상치 샘플 (가격 > Q95):")
print("-"*70)

for _, row in suspicious.head(5).iterrows():
    model, year, q95 = row['Model'], row['YearOnly'], row['Q95']
    outliers = df[(df['Model']==model) & (df['YearOnly']==year) & (df['Price'] > q95 * 1.5)]
    if len(outliers) > 0:
        print(f"\n{model} {year}년 (Q95={q95:,.0f}만원):")
        print(outliers[['Manufacturer', 'Model', 'Year', 'Mileage', 'Price']].head(5).to_string())

# 이상치 제거 시뮬레이션
print(f"\n" + "="*70)
print("💡 이상치 제거 시뮬레이션")
print("="*70)

# 방법 1: 고정 값 제거 (9999 등)
fixed_outliers = len(df[df['Price'].isin([9999, 11111, 99999, 1111])])
print(f"방법1 - 고정값(9999 등) 제거: {fixed_outliers:,}건")

# 방법 2: 모델+연식별 Q95 초과 제거
def count_outliers_q95(df):
    outlier_mask = pd.Series(False, index=df.index)
    for (model, year), group in df.groupby(['Model', 'YearOnly']):
        q95 = group['Price'].quantile(0.95)
        threshold = q95 * 1.3  # Q95의 1.3배 초과
        mask = (df['Model']==model) & (df['YearOnly']==year) & (df['Price'] > threshold)
        outlier_mask = outlier_mask | mask
    return outlier_mask.sum()

q95_outliers = count_outliers_q95(df)
print(f"방법2 - Q95*1.3 초과 제거: {q95_outliers:,}건")

# 방법 3: 두 방법 조합
combined = len(df[df['Price'].isin([9999, 11111, 99999, 1111])]) + q95_outliers
print(f"방법3 - 조합: 약 {combined:,}건 (중복 있을 수 있음)")
