"""전체 차종 무작위 테스트"""
import pandas as pd
import numpy as np
import requests
import random

API_URL = "http://localhost:8000/api/predict"

print("="*70)
print("🚗 전체 차종 무작위 테스트")
print("="*70)

# 패턴 이상치
pattern_prices = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]

# ========== 1. 국산차 (제네시스 포함) ==========
print("\n📊 1. 국산차 전체 테스트")
print("-"*70)

df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Model', 'Manufacturer'])
df = df[df['Price'] > 100]
df = df[~df['Price'].isin(pattern_prices)]
df['YearOnly'] = (df['Year'] // 100).astype(int)
df = df[df['YearOnly'] >= 2018]  # 최근 7년

# 중복 제거
df = df.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')

# 모델별로 그룹화해서 테스트
models = df.groupby('Model').agg({
    'Price': ['mean', 'count'],
    'Manufacturer': 'first'
}).reset_index()
models.columns = ['Model', 'avg_price', 'count', 'Manufacturer']
models = models[models['count'] >= 20]  # 데이터 20개 이상인 모델만
models = models.sort_values('count', ascending=False)

print(f"테스트 대상 모델: {len(models)}개")

# 상위 50개 모델 테스트
test_models = models.head(50)
domestic_results = []

for _, row in test_models.iterrows():
    model_name = row['Model']
    brand = row['Manufacturer']
    
    # 해당 모델의 샘플 데이터
    samples = df[df['Model'] == model_name]
    if len(samples) < 5:
        continue
    
    # 중앙값 기준 샘플 선택
    median_idx = samples['Price'].sub(samples['Price'].median()).abs().idxmin()
    sample = samples.loc[median_idx]
    
    year = int(sample['YearOnly'])
    mileage = int(sample['Mileage'])
    actual = sample['Price']
    
    try:
        # 실제 옵션 데이터 추출
        req_data = {
            'brand': brand,
            'model': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': '가솔린',
            'has_sunroof': bool(sample.get('has_sunroof', 0)) if pd.notna(sample.get('has_sunroof')) else None,
            'has_navigation': bool(sample.get('has_navigation', 0)) if pd.notna(sample.get('has_navigation')) else None,
            'has_leather_seat': bool(sample.get('has_leather_seat', 0)) if pd.notna(sample.get('has_leather_seat')) else None,
            'has_smart_key': bool(sample.get('has_smart_key', 0)) if pd.notna(sample.get('has_smart_key')) else None,
            'has_rear_camera': bool(sample.get('has_rear_camera', 0)) if pd.notna(sample.get('has_rear_camera')) else None,
            'has_led_lamp': bool(sample.get('has_led_lamp', 0)) if pd.notna(sample.get('has_led_lamp')) else None,
            'has_heated_seat': bool(sample.get('has_heated_seat', 0)) if pd.notna(sample.get('has_heated_seat')) else None,
            'has_ventilated_seat': bool(sample.get('has_ventilated_seat', 0)) if pd.notna(sample.get('has_ventilated_seat')) else None,
        }
        
        resp = requests.post(API_URL, json=req_data, timeout=5)
        
        if resp.status_code == 200:
            pred = resp.json()['predicted_price']
            error = abs(pred - actual) / actual * 100
            domestic_results.append({
                'model': model_name,
                'brand': brand,
                'year': year,
                'actual': actual,
                'pred': pred,
                'error': error
            })
    except:
        pass

# 결과 정렬 및 출력
domestic_df = pd.DataFrame(domestic_results)
domestic_df = domestic_df.sort_values('error')

print(f"\n✅ 테스트 완료: {len(domestic_df)}개 모델")
print(f"\n오차율 상위 10개 (좋음):")
for _, r in domestic_df.head(10).iterrows():
    print(f"  ✅ {r['model']} {r['year']}년: 예측 {r['pred']:,.0f} / 실제 {r['actual']:,.0f} (오차 {r['error']:.1f}%)")

print(f"\n오차율 하위 10개 (나쁨):")
for _, r in domestic_df.tail(10).iterrows():
    status = "⚠️" if r['error'] < 25 else "❌"
    print(f"  {status} {r['model']} {r['year']}년: 예측 {r['pred']:,.0f} / 실제 {r['actual']:,.0f} (오차 {r['error']:.1f}%)")

print(f"\n📈 국산차 통계:")
print(f"  평균 오차: {domestic_df['error'].mean():.1f}%")
print(f"  중앙값 오차: {domestic_df['error'].median():.1f}%")
print(f"  오차 10% 이내: {len(domestic_df[domestic_df['error']<=10])}/{len(domestic_df)} ({len(domestic_df[domestic_df['error']<=10])/len(domestic_df)*100:.0f}%)")
print(f"  오차 15% 이내: {len(domestic_df[domestic_df['error']<=15])}/{len(domestic_df)} ({len(domestic_df[domestic_df['error']<=15])/len(domestic_df)*100:.0f}%)")
print(f"  오차 25% 이내: {len(domestic_df[domestic_df['error']<=25])}/{len(domestic_df)} ({len(domestic_df[domestic_df['error']<=25])/len(domestic_df)*100:.0f}%)")

# ========== 2. 수입차 ==========
print("\n" + "="*70)
print("📊 2. 수입차 전체 테스트")
print("-"*70)

df_i = pd.read_csv('encar_imported_data.csv')
df_i_detail = pd.read_csv('data/complete_imported_details.csv')
df_i = df_i.merge(df_i_detail, left_on='Id', right_on='car_id', how='inner')
df_i = df_i.dropna(subset=['Price', 'Mileage', 'Year', 'Model', 'Manufacturer'])
df_i = df_i[df_i['Price'] > 300]
df_i = df_i[~df_i['Price'].isin(pattern_prices)]
df_i['YearOnly'] = (df_i['Year'] // 100).astype(int)
df_i = df_i[df_i['YearOnly'] >= 2018]
df_i = df_i.drop_duplicates(subset=['Model', 'Year', 'Mileage', 'Price'], keep='first')

# 모델별 그룹화
models_i = df_i.groupby('Model').agg({
    'Price': ['mean', 'count'],
    'Manufacturer': 'first'
}).reset_index()
models_i.columns = ['Model', 'avg_price', 'count', 'Manufacturer']
models_i = models_i[models_i['count'] >= 20]
models_i = models_i.sort_values('count', ascending=False)

print(f"테스트 대상 모델: {len(models_i)}개")

test_models_i = models_i.head(50)
imported_results = []

for _, row in test_models_i.iterrows():
    model_name = row['Model']
    brand = row['Manufacturer']
    
    samples = df_i[df_i['Model'] == model_name]
    if len(samples) < 5:
        continue
    
    median_idx = samples['Price'].sub(samples['Price'].median()).abs().idxmin()
    sample = samples.loc[median_idx]
    
    year = int(sample['YearOnly'])
    mileage = int(sample['Mileage'])
    actual = sample['Price']
    
    try:
        # 실제 옵션 데이터 추출
        req_data = {
            'brand': brand,
            'model': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': '가솔린',
            'has_sunroof': bool(sample.get('has_sunroof', 0)) if pd.notna(sample.get('has_sunroof')) else None,
            'has_navigation': bool(sample.get('has_navigation', 0)) if pd.notna(sample.get('has_navigation')) else None,
            'has_leather_seat': bool(sample.get('has_leather_seat', 0)) if pd.notna(sample.get('has_leather_seat')) else None,
            'has_smart_key': bool(sample.get('has_smart_key', 0)) if pd.notna(sample.get('has_smart_key')) else None,
            'has_rear_camera': bool(sample.get('has_rear_camera', 0)) if pd.notna(sample.get('has_rear_camera')) else None,
            'has_led_lamp': bool(sample.get('has_led_lamp', 0)) if pd.notna(sample.get('has_led_lamp')) else None,
            'has_heated_seat': bool(sample.get('has_heated_seat', 0)) if pd.notna(sample.get('has_heated_seat')) else None,
            'has_ventilated_seat': bool(sample.get('has_ventilated_seat', 0)) if pd.notna(sample.get('has_ventilated_seat')) else None,
        }
        
        resp = requests.post(API_URL, json=req_data, timeout=5)
        
        if resp.status_code == 200:
            pred = resp.json()['predicted_price']
            error = abs(pred - actual) / actual * 100
            imported_results.append({
                'model': model_name,
                'brand': brand,
                'year': year,
                'actual': actual,
                'pred': pred,
                'error': error
            })
    except:
        pass

imported_df = pd.DataFrame(imported_results)
imported_df = imported_df.sort_values('error')

print(f"\n✅ 테스트 완료: {len(imported_df)}개 모델")
print(f"\n오차율 상위 10개 (좋음):")
for _, r in imported_df.head(10).iterrows():
    print(f"  ✅ {r['brand']} {r['model']} {r['year']}년: 예측 {r['pred']:,.0f} / 실제 {r['actual']:,.0f} (오차 {r['error']:.1f}%)")

print(f"\n오차율 하위 10개 (나쁨):")
for _, r in imported_df.tail(10).iterrows():
    status = "⚠️" if r['error'] < 25 else "❌"
    print(f"  {status} {r['brand']} {r['model']} {r['year']}년: 예측 {r['pred']:,.0f} / 실제 {r['actual']:,.0f} (오차 {r['error']:.1f}%)")

print(f"\n📈 수입차 통계:")
print(f"  평균 오차: {imported_df['error'].mean():.1f}%")
print(f"  중앙값 오차: {imported_df['error'].median():.1f}%")
print(f"  오차 10% 이내: {len(imported_df[imported_df['error']<=10])}/{len(imported_df)} ({len(imported_df[imported_df['error']<=10])/len(imported_df)*100:.0f}%)")
print(f"  오차 15% 이내: {len(imported_df[imported_df['error']<=15])}/{len(imported_df)} ({len(imported_df[imported_df['error']<=15])/len(imported_df)*100:.0f}%)")
print(f"  오차 25% 이내: {len(imported_df[imported_df['error']<=25])}/{len(imported_df)} ({len(imported_df[imported_df['error']<=25])/len(imported_df)*100:.0f}%)")

# ========== 종합 ==========
print("\n" + "="*70)
print("📈 종합 결과")
print("="*70)

all_results = pd.concat([domestic_df, imported_df])
print(f"\n총 테스트: {len(all_results)}개 모델")
print(f"전체 평균 오차: {all_results['error'].mean():.1f}%")
print(f"전체 중앙값 오차: {all_results['error'].median():.1f}%")
print(f"오차 10% 이내: {len(all_results[all_results['error']<=10])}/{len(all_results)} ({len(all_results[all_results['error']<=10])/len(all_results)*100:.0f}%)")
print(f"오차 15% 이내: {len(all_results[all_results['error']<=15])}/{len(all_results)} ({len(all_results[all_results['error']<=15])/len(all_results)*100:.0f}%)")
print(f"오차 25% 이내: {len(all_results[all_results['error']<=25])}/{len(all_results)} ({len(all_results[all_results['error']<=25])/len(all_results)*100:.0f}%)")
