"""실제 데이터와 예측 값 비교"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, 'ml-service/services')
from prediction_v11 import PredictionServiceV11

# 예측 서비스 초기화
ps = PredictionServiceV11()

# 실제 데이터 로드
df = pd.read_csv('data/encar_raw_domestic.csv')

# Year 형식 변환 (202408 -> 2024)
df['Year'] = df['Year'].astype(str).str[:4].astype(int)

# 이상치 제거 (가격 100만원 미만, 9000만원 초과)
df = df[(df['Price'] >= 100) & (df['Price'] <= 9000)]

print(f'전체 데이터: {len(df):,}건')

# 그랜저 데이터 필터링
granger = df[df['Model'].str.contains('그랜저', na=False)].copy()
print(f'그랜저 전체: {len(granger):,}건')

# 연식별 분석
print('\n' + '='*60)
print('📊 연식별 실제 가격 vs 예측 가격')
print('='*60)

for year in [2024, 2023, 2022, 2021, 2020]:
    year_data = granger[granger['Year'] == year]
    if len(year_data) == 0:
        continue
    
    # 실제 데이터 통계
    actual_mean = year_data['Price'].mean()
    actual_median = year_data['Price'].median()
    avg_mileage = year_data['Mileage'].mean()
    
    # 가장 많은 모델명 찾기
    top_model = year_data['Model'].value_counts().index[0]
    
    # 예측 (평균 주행거리 기준)
    pred = ps.predict('현대', top_model, year, int(avg_mileage), fuel='가솔린')
    
    diff = pred.predicted_price - actual_mean
    diff_pct = (diff / actual_mean) * 100
    
    print(f'\n[{year}년식] (샘플: {len(year_data)}건, 평균 {avg_mileage/10000:.1f}만km)')
    print(f'  대표 모델: {top_model}')
    print(f'  실제 평균: {actual_mean:,.0f}만원')
    print(f'  실제 중앙값: {actual_median:,.0f}만원')
    print(f'  예측 가격: {pred.predicted_price:,.0f}만원')
    print(f'  차이: {diff:+,.0f}만원 ({diff_pct:+.1f}%)')

# 연료별 분석
print('\n' + '='*60)
print('📊 연료별 실제 가격 비교 (2022년식 기준)')
print('='*60)

year_2022 = granger[granger['Year'] == 2022]
if 'FuelType' in year_2022.columns:
    fuel_map = {'가솔린': '가솔린', '디젤': '디젤', '하이브리드': '하이브리드', 'LPG': 'LPG', 'LPG(일반인 구입)': 'LPG'}
    for fuel_type, fuel_name in [('가솔린', '가솔린'), ('하이브리드', '하이브리드'), ('LPG', 'LPG')]:
        fuel_data = year_2022[year_2022['FuelType'].str.contains(fuel_type, na=False)]
        if len(fuel_data) > 0:
            actual = fuel_data['Price'].mean()
            avg_mile = fuel_data['Mileage'].mean()
            top_model = fuel_data['Model'].value_counts().index[0]
            pred = ps.predict('현대', top_model, 2022, int(avg_mile), fuel=fuel_name)
            diff = pred.predicted_price - actual
            print(f'{fuel_name:6}: 실제 {actual:>5,.0f}만원, 예측 {pred.predicted_price:>5,.0f}만원 (차이: {diff:+5,.0f}) [{len(fuel_data)}건]')

# 샘플 비교
print('\n' + '='*60)
print('📊 랜덤 샘플 15건 비교')
print('='*60)

sample = granger.sample(min(20, len(granger)), random_state=42)
errors = []
for _, row in sample.iterrows():
    model = row['Model']
    year = row['Year']
    mileage = row['Mileage']
    actual = row['Price']
    fuel_type = str(row.get('FuelType', '가솔린'))
    
    # 연료 타입 매핑 (모델명에서도 확인)
    if '하이브리드' in model or '하이브리드' in fuel_type:
        fuel = '하이브리드'
    elif 'LPG' in fuel_type:
        fuel = 'LPG'
    elif '디젤' in fuel_type:
        fuel = '디젤'
    else:
        fuel = '가솔린'
    
    pred = ps.predict('현대', model, year, mileage, fuel=fuel)
    error = pred.predicted_price - actual
    error_pct = (error / actual) * 100
    errors.append(abs(error_pct))
    
    model_short = model[:18] if len(model) > 18 else model
    print(f'{model_short:18} {year}년 {mileage/10000:>4.1f}만km {fuel:6} | 실제:{actual:>5,.0f} 예측:{pred.predicted_price:>5,.0f} | {error:+5,.0f}만원 ({error_pct:+5.1f}%)')

print(f'\n📈 평균 절대 오차율(MAPE): {np.mean(errors):.1f}%')
print(f'📈 중앙값 오차율: {np.median(errors):.1f}%')
print(f'📈 10% 이내 정확도: {sum(1 for e in errors if e <= 10) / len(errors) * 100:.0f}%')
print(f'📈 20% 이내 정확도: {sum(1 for e in errors if e <= 20) / len(errors) * 100:.0f}%')
