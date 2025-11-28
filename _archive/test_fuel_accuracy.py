"""연료별 가격 정확도 테스트"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, 'ml-service/services')
from prediction_v12 import PredictionServiceV12

ps = PredictionServiceV12()

df = pd.read_csv('data/encar_raw_domestic.csv')
df['YearOnly'] = (df['Year'] // 100).astype(int)

def normalize_fuel(f):
    f = str(f).lower()
    if '하이브리드' in f: return '하이브리드'
    elif 'lpg' in f: return 'LPG'
    elif '디젤' in f: return '디젤'
    return '가솔린'

df['Fuel'] = df['FuelType'].apply(normalize_fuel)
df = df[(df['Price'] >= 100) & (df['Price'] <= 9000)]

print('='*70)
print('📊 1. 실제 연료별 가격 비율 분석 (더 뉴 그랜저 IG 2022년)')
print('='*70)

ig = df[(df['Model'] == '더 뉴 그랜저 IG') & (df['YearOnly'] == 2022)]
ig_filtered = ig[(ig['Mileage'] >= 50000) & (ig['Mileage'] <= 80000)]

print('\n[동일 주행거리 5-8만km]')
for fuel in ['가솔린', 'LPG']:
    fd = ig_filtered[ig_filtered['Fuel'] == fuel]
    if len(fd) > 0:
        print(f'{fuel}: 평균 {fd["Price"].mean():.0f}만원 ({len(fd)}건)')

gas_data = ig_filtered[ig_filtered['Fuel'] == '가솔린']
lpg_data = ig_filtered[ig_filtered['Fuel'] == 'LPG']

if len(gas_data) > 0 and len(lpg_data) > 0:
    gas_price = gas_data['Price'].mean()
    lpg_price = lpg_data['Price'].mean()
    actual_ratio = lpg_price / gas_price
    actual_discount = (1 - actual_ratio) * 100
    print(f'\n실제 LPG 할인율: -{actual_discount:.1f}%')
    print(f'현재 적용 할인율: -12.0%')

# 전체 그랜저 연료별 비율
print('\n' + '='*70)
print('📊 2. 전체 그랜저 연료별 가격 비율')
print('='*70)

granger = df[df['Model'].str.contains('그랜저', na=False)]
fuel_stats = granger.groupby('Fuel')['Price'].mean()
gas_avg = fuel_stats.get('가솔린', 1)

for fuel in ['가솔린', 'LPG', '디젤', '하이브리드']:
    if fuel in fuel_stats.index:
        ratio = fuel_stats[fuel] / gas_avg
        discount = (ratio - 1) * 100
        print(f'{fuel:10}: 평균 {fuel_stats[fuel]:,.0f}만원 (가솔린 대비 {discount:+.1f}%)')

# 예측 정확도 테스트
print('\n' + '='*70)
print('📊 3. 랜덤 샘플 20건 예측 정확도')
print('='*70)

sample = granger.sample(min(20, len(granger)), random_state=123)
errors = []

for _, row in sample.iterrows():
    model = row['Model']
    year = row['YearOnly']
    mileage = int(row['Mileage'])
    actual = row['Price']
    fuel = row['Fuel']
    
    try:
        pred = ps.predict('현대', model, year, mileage, fuel=fuel)
        error = pred.predicted_price - actual
        error_pct = abs(error / actual) * 100
        errors.append(error_pct)
        
        status = '✅' if error_pct <= 15 else '⚠️'
        print(f'{model[:18]:18} {year}년 {mileage/10000:>4.1f}만km {fuel:6} | 실제:{actual:>5,.0f} 예측:{pred.predicted_price:>5,.0f} | {error:+5,.0f}만원 ({error/actual*100:+5.1f}%) {status}')
    except Exception as e:
        print(f'{model[:18]:18} - 예측 실패: {e}')

if errors:
    print(f'\n📈 MAPE: {np.mean(errors):.1f}%')
    print(f'📈 15% 이내 정확도: {sum(1 for e in errors if e <= 15) / len(errors) * 100:.0f}%')
