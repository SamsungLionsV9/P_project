"""차량 이미지가 필요한 목록"""
import pandas as pd

# 데이터 로드
domestic = pd.read_csv('data/encar_raw_domestic.csv')
imported = pd.read_csv('data/encar_imported_data.csv')

print('='*70)
print('🚗 차량 이미지 필요 목록 (등록 대수 기준)')
print('='*70)

# 국산차 인기 모델
print('\n📊 국산차 TOP 20 (이미지 필요)')
print('-'*70)
domestic_top = domestic.groupby(['Manufacturer', 'Model']).size().reset_index(name='count')
domestic_top = domestic_top.sort_values('count', ascending=False).head(20)
for idx, (i, row) in enumerate(domestic_top.iterrows(), 1):
    print(f'  {idx:2}. {row["Manufacturer"]} {row["Model"]}: {row["count"]:,}대')

# 외제차 인기 모델
print('\n📊 외제차 TOP 15 (이미지 필요)')
print('-'*70)
imported_top = imported.groupby(['Manufacturer', 'Model']).size().reset_index(name='count')
imported_top = imported_top.sort_values('count', ascending=False).head(15)
for idx, (i, row) in enumerate(imported_top.iterrows(), 1):
    print(f'  {idx:2}. {row["Manufacturer"]} {row["Model"]}: {row["count"]:,}대')

# 브랜드별 로고 필요
print('\n🏷️ 브랜드 로고 필요')
print('-'*70)
domestic_brands = domestic['Manufacturer'].unique()
imported_brands = imported['Manufacturer'].unique()
print(f'  국산: {", ".join(sorted(domestic_brands))}')
print(f'  외제: {", ".join(sorted(imported_brands)[:10])}...')

print('\n' + '='*70)
total = len(domestic_top) + len(imported_top)
print(f'📌 총 이미지 필요: 국산 {len(domestic_top)}개 + 외제 {len(imported_top)}개 = {total}개 차량 이미지')
print(f'📌 브랜드 로고: 국산 {len(domestic_brands)}개 + 외제 {len(imported_brands)}개')
print('='*70)
