import pandas as pd

df = pd.read_csv('data/processed_encar_combined.csv')
domestic = df[df['car_type'] == 'Domestic']

print('='*70)
print('국산차 가격 분포 분석')
print('='*70)

print(f'\n전체 국산차: {len(domestic):,}건')
print(f'\n가격대별 분포:')
print(f'  5000만원 초과:    {len(domestic[domestic["price"] > 5000]):,}건')
print(f'  4000-5000만원:    {len(domestic[(domestic["price"] > 4000) & (domestic["price"] <= 5000)]):,}건')
print(f'  3000-4000만원:    {len(domestic[(domestic["price"] > 3000) & (domestic["price"] <= 4000)]):,}건')
print(f'  2000-3000만원:    {len(domestic[(domestic["price"] > 2000) & (domestic["price"] <= 3000)]):,}건')

print(f'\n📊 5000만원 초과 차량 상위 20개:')
high_price = domestic[domestic['price'] > 5000].sort_values('price', ascending=False)
print(high_price[['brand', 'model_name', 'year', 'mileage', 'price']].head(20).to_string(index=False))

print(f'\n📊 브랜드별 고가 차량 (5000만원 이상):')
if len(high_price) > 0:
    print(high_price['brand'].value_counts())

print(f'\n📊 4000-5000만원 차량 예시:')
mid_high = domestic[(domestic['price'] > 4000) & (domestic['price'] <= 5000)]
print(mid_high[['brand', 'model_name', 'year', 'mileage', 'price']].head(15).to_string(index=False))

print(f'\n결론:')
removed = len(domestic[domestic['price'] > 5000])
total = len(domestic)
print(f'  - 제거된 데이터: {removed:,}건 ({removed/total*100:.2f}%)')
print(f'  - 이들은 정상적인 고급 국산차일 가능성 높음')
print(f'  - 제네시스, 팰리세이드, 카니발 등 포함')
