"""옵션 추가 시 예측 정확도 비교"""
import pandas as pd
import numpy as np
import requests

API_URL = "http://localhost:8000/api/predict"

print("="*70)
print("🔍 옵션 추가 시 예측 정확도 비교")
print("="*70)

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 패턴/이상치 제거
patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]
df = df[df['Price'] > 100]
df = df[df['YearOnly'] >= 2020]

# 테스트 모델들
test_models = [
    ('더 뉴 그랜저 IG', 2022, '현대'),
    ('K5 3세대', 2022, '기아'),
    ('쏘나타 (DN8)', 2022, '현대'),
    ('GV80', 2021, '제네시스'),
    ('GV70', 2022, '제네시스'),
]

results_no_option = []
results_with_option = []

for model_name, year, brand in test_models:
    # 해당 모델 데이터
    subset = df[(df['Model']==model_name) & (df['YearOnly']==year)]
    if len(subset) < 10:
        continue
    
    # 10개 샘플 테스트
    samples = subset.sample(min(10, len(subset)), random_state=42)
    
    for _, row in samples.iterrows():
        actual = row['Price']
        mileage = int(row['Mileage'])
        
        # 1. 옵션 없이 예측
        base_req = {
            'brand': brand,
            'model': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': '가솔린'
        }
        try:
            resp = requests.post(API_URL, json=base_req, timeout=5)
            pred_no_opt = resp.json()['predicted_price']
            error_no_opt = abs(pred_no_opt - actual) / actual * 100
            results_no_option.append(error_no_opt)
        except:
            continue
        
        # 2. 실제 옵션 넣어서 예측
        opt_req = {
            **base_req,
            'has_sunroof': bool(row.get('has_sunroof', 0)),
            'has_navigation': bool(row.get('has_navigation', 0)),
            'has_leather_seat': bool(row.get('has_leather_seat', 0)),
            'has_smart_key': bool(row.get('has_smart_key', 0)),
            'has_rear_camera': bool(row.get('has_rear_camera', 0)),
            'has_led_lamp': bool(row.get('has_led_lamp', 0)),
            'has_heated_seat': bool(row.get('has_heated_seat', 0)),
            'has_ventilated_seat': bool(row.get('has_ventilated_seat', 0)),
            'is_accident_free': True  # 데이터에 무사고 정보 없음
        }
        try:
            resp = requests.post(API_URL, json=opt_req, timeout=5)
            pred_with_opt = resp.json()['predicted_price']
            error_with_opt = abs(pred_with_opt - actual) / actual * 100
            results_with_option.append(error_with_opt)
        except:
            continue

print(f"\n테스트 샘플: {len(results_no_option)}개")

print("\n" + "="*70)
print("📊 결과 비교")
print("="*70)

print(f"\n옵션 미입력 (기본값):")
print(f"  평균 오차: {np.mean(results_no_option):.1f}%")
print(f"  중앙값 오차: {np.median(results_no_option):.1f}%")
print(f"  10% 이내: {sum(1 for e in results_no_option if e <= 10)/len(results_no_option)*100:.0f}%")

print(f"\n실제 옵션 입력:")
print(f"  평균 오차: {np.mean(results_with_option):.1f}%")
print(f"  중앙값 오차: {np.median(results_with_option):.1f}%")
print(f"  10% 이내: {sum(1 for e in results_with_option if e <= 10)/len(results_with_option)*100:.0f}%")

improvement = np.mean(results_no_option) - np.mean(results_with_option)
print(f"\n✅ 개선 효과: {improvement:+.1f}% 포인트")

if improvement > 0:
    print("👍 옵션 입력 시 예측이 더 정확해집니다!")
else:
    print("⚠️ 옵션 입력이 예측 정확도에 큰 영향을 주지 않습니다.")
