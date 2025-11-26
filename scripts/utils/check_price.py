import pandas as pd
df = pd.read_csv('encar_raw_domestic.csv')
df['YearOnly'] = (df['Year']//100).astype(int)
granger = df[df['Model'].str.contains('그랜저', na=False)]
print('=== 그랜저 연도별 평균 가격 ===')
for y in [2024, 2023, 2022, 2021, 2020]:
    g = granger[granger['YearOnly']==y]
    if len(g) > 0:
        print(f"{y}년식: {g['Price'].mean():,.0f}만원 (n={len(g)})")

k5 = df[df['Model'].str.contains('K5', na=False)]
print('\n=== K5 연도별 평균 가격 ===')
for y in [2024, 2023, 2022, 2021, 2020]:
    k = k5[k5['YearOnly']==y]
    if len(k) > 0:
        print(f"{y}년식: {k['Price'].mean():,.0f}만원 (n={len(k)})")
