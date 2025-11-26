"""모든 모델 (국산차, 제네시스, 수입차) 실제값 vs 예측값 테스트"""
import requests
import pandas as pd
import numpy as np

print("="*70)
print("🚗 전체 모델 실제 서비스 수준 평가")
print("="*70)

# ========== 1. 국산차 테스트 ==========
print("\n" + "="*70)
print("📊 1. 국산차 모델 (V2)")
print("="*70)

df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
genesis_mask = df['Manufacturer'].str.contains('제네시스|GENESIS', case=False, na=False)
df_domestic = df[~genesis_mask]
df_domestic = df_domestic[df_domestic['Price'] > 100]
# 패턴 이상치 제거
pattern_prices = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df_domestic = df_domestic[~df_domestic['Price'].isin(pattern_prices)]
df_domestic['YearOnly'] = (df_domestic['Year'] // 100).astype(int)

domestic_tests = [
    ('더 뉴 그랜저 IG', 2022, 35000, '가솔린', '현대'),
    ('K5 3세대', 2022, 30000, '가솔린', '기아'),
    ('쏘나타 (DN8)', 2022, 40000, '가솔린', '현대'),
    ('카니발 4세대', 2022, 45000, '디젤', '기아'),
    ('싼타페 (MX5)', 2023, 30000, '디젤', '현대'),
    ('캐스퍼', 2023, 20000, '가솔린', '현대'),
]

domestic_results = []
for model_name, year, mileage, fuel, brand in domestic_tests:
    subset = df_domestic[(df_domestic['Model']==model_name) & (df_domestic['YearOnly']==year) & 
                         (df_domestic['Mileage']>=mileage-15000) & (df_domestic['Mileage']<=mileage+15000)]
    if len(subset) < 3:
        continue
    actual = subset['Price'].mean()
    
    try:
        r = requests.post('http://localhost:8000/api/predict', json={
            'brand': brand, 'model': model_name, 'year': year, 'mileage': mileage, 'fuel': fuel
        }, timeout=5)
        if r.status_code == 200:
            pred = r.json()['predicted_price']
            error = abs(pred - actual) / actual * 100
            status = "✅" if error < 15 else ("⚠️" if error < 25 else "❌")
            print(f"{status} {model_name} {year}년: 예측 {pred:,.0f}만원 / 실제 {actual:,.0f}만원 (오차 {error:.1f}%)")
            domestic_results.append(error)
    except:
        pass

if domestic_results:
    print(f"\n국산차 평균 오차: {np.mean(domestic_results):.1f}%")

# ========== 2. 제네시스 테스트 ==========
print("\n" + "="*70)
print("📊 2. 제네시스 모델 (국산차 통합)")
print("="*70)

# 제네시스는 국산차 데이터에서 필터링 (이제 국산차로 통합됨)
df_genesis = df[df['Manufacturer'].str.contains('제네시스|GENESIS|Genesis', case=False, na=False)]
df_genesis = df_genesis[df_genesis['Price'] > 100]
df_genesis = df_genesis[~df_genesis['Price'].isin(pattern_prices)]  # 패턴 이상치 제거
df_genesis['YearOnly'] = (df_genesis['Year'] // 100).astype(int)

genesis_tests = [
    ('G80 (RG3)', 2021, 50000, '가솔린', '제네시스'),
    ('G80 (RG3)', 2022, 35000, '가솔린', '제네시스'),
    ('GV80', 2021, 45000, '디젤', '제네시스'),
    ('GV80', 2022, 30000, '디젤', '제네시스'),
    ('더 뉴 G70', 2021, 40000, '가솔린', '제네시스'),
    ('GV70', 2022, 35000, '가솔린', '제네시스'),
]

genesis_results = []
for model_name, year, mileage, fuel, brand in genesis_tests:
    subset = df_genesis[(df_genesis['Model'].str.contains(model_name, na=False)) & (df_genesis['YearOnly']==year) & 
                        (df_genesis['Mileage']>=mileage-20000) & (df_genesis['Mileage']<=mileage+20000)]
    if len(subset) < 3:
        print(f"   {model_name} {year}년: 데이터 부족 (n={len(subset)})")
        continue
    actual = subset['Price'].mean()
    
    try:
        r = requests.post('http://localhost:8000/api/predict', json={
            'brand': brand, 'model': model_name, 'year': year, 'mileage': mileage, 'fuel': fuel
        }, timeout=5)
        if r.status_code == 200:
            pred = r.json()['predicted_price']
            error = abs(pred - actual) / actual * 100
            status = "✅" if error < 15 else ("⚠️" if error < 25 else "❌")
            print(f"{status} {model_name} {year}년: 예측 {pred:,.0f}만원 / 실제 {actual:,.0f}만원 (오차 {error:.1f}%)")
            genesis_results.append(error)
    except Exception as e:
        print(f"   {model_name}: 에러 - {e}")

if genesis_results:
    print(f"\n제네시스 평균 오차: {np.mean(genesis_results):.1f}%")
else:
    print("제네시스 테스트 데이터 부족")

# ========== 3. 수입차 테스트 ==========
print("\n" + "="*70)
print("📊 3. 수입차 모델")
print("="*70)

try:
    df_imported = pd.read_csv('encar_imported_data.csv')
    df_imported_detail = pd.read_csv('data/complete_imported_details.csv')
    df_i = df_imported.merge(df_imported_detail, left_on='Id', right_on='car_id', how='inner')
except:
    # 대체 경로 시도
    df_i = pd.read_csv('data/encar_detailed_imported.csv')
    
df_i = df_i[df_i['Price'] > 100]
df_i = df_i[~df_i['Price'].isin([9999, 99999, 11111])]  # 이상치 제거
df_i['YearOnly'] = (df_i['Year'] // 100).astype(int)

imported_tests = [
    ('E-클래스 W213', 2020, 50000, '가솔린', '벤츠'),
    ('E-클래스 W213', 2021, 40000, '가솔린', '벤츠'),
    ('5시리즈 (G30)', 2020, 55000, '가솔린', 'BMW'),
    ('5시리즈 (G30)', 2021, 40000, '가솔린', 'BMW'),
    ('A6 (C8)', 2020, 50000, '가솔린', '아우디'),
    ('C-클래스 W205', 2020, 40000, '가솔린', '벤츠'),
    ('3시리즈 (G20)', 2021, 40000, '가솔린', 'BMW'),
    ('X5 (G05)', 2021, 45000, '디젤', 'BMW'),
    ('GLE-클래스 W167', 2021, 40000, '디젤', '벤츠'),
]

imported_results = []
for model_name, year, mileage, fuel, brand in imported_tests:
    subset = df_i[(df_i['Model'].str.contains(model_name, na=False)) & (df_i['YearOnly']==year) & 
                  (df_i['Mileage']>=mileage-20000) & (df_i['Mileage']<=mileage+20000)]
    if len(subset) < 3:
        continue
    actual = subset['Price'].mean()
    
    try:
        r = requests.post('http://localhost:8000/api/predict', json={
            'brand': brand, 'model': model_name, 'year': year, 'mileage': mileage, 'fuel': fuel
        }, timeout=5)
        if r.status_code == 200:
            pred = r.json()['predicted_price']
            error = abs(pred - actual) / actual * 100
            status = "✅" if error < 15 else ("⚠️" if error < 25 else "❌")
            print(f"{status} {brand} {model_name} {year}년: 예측 {pred:,.0f}만원 / 실제 {actual:,.0f}만원 (오차 {error:.1f}%)")
            imported_results.append(error)
    except Exception as e:
        print(f"   {brand} {model_name}: 에러 - {e}")

if imported_results:
    print(f"\n수입차 평균 오차: {np.mean(imported_results):.1f}%")

# ========== 종합 요약 ==========
print("\n" + "="*70)
print("📈 종합 요약")
print("="*70)

all_results = domestic_results + genesis_results + imported_results
if all_results:
    print(f"총 테스트: {len(all_results)}개")
    print(f"전체 평균 오차: {np.mean(all_results):.1f}%")
    print(f"오차 15% 이내: {len([e for e in all_results if e < 15])}개 ({len([e for e in all_results if e < 15])/len(all_results)*100:.0f}%)")
    print(f"오차 25% 이내: {len([e for e in all_results if e < 25])}개 ({len([e for e in all_results if e < 25])/len(all_results)*100:.0f}%)")
    
    print("\n모델별 평균 오차:")
    if domestic_results:
        print(f"  - 국산차: {np.mean(domestic_results):.1f}%")
    if genesis_results:
        print(f"  - 제네시스: {np.mean(genesis_results):.1f}%")
    if imported_results:
        print(f"  - 수입차: {np.mean(imported_results):.1f}%")
