import pandas as pd
df = pd.read_csv('encar_raw_domestic.csv')
df['YearOnly'] = (df['Year']//100).astype(int)

# 더 뉴 그랜저 IG 2022
g = df[(df['Model']=='더 뉴 그랜저 IG') & (df['YearOnly']==2022) & (df['Mileage']>=30000) & (df['Mileage']<=40000)]
print(f"더 뉴 그랜저 IG 2022 (30-40k): 평균 {g['Price'].mean():,.0f}만원 (n={len(g)})")

# K5 3세대 2022
k = df[(df['Model']=='K5 3세대') & (df['YearOnly']==2022) & (df['Mileage']>=25000) & (df['Mileage']<=35000)]
print(f"K5 3세대 2022 (25-35k): 평균 {k['Price'].mean():,.0f}만원 (n={len(k)})")
