"""15~20% 오차 케이스 - 옵션 차이인지 확인"""
import pandas as pd
import numpy as np
import requests

API_URL = "http://localhost:8000/api/predict"

print("="*70)
print("🔍 15~20% 오차 케이스 - 옵션이 원인인지 확인")
print("="*70)

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)

patterns = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999, 99999]
df = df[~df['Price'].isin(patterns)]
df = df[df['Price'] > 100]

# 오차 높은 모델들
high_error_models = [
    ('스포티지 5세대', 2021, '기아'),  # 20% 오차
    ('베리 뉴 티볼리', 2021, 'KG모빌리티(쌍용)'),  # 19% 오차
    ('더 K9', 2019, '기아'),  # 17.5% 오차
    ('K8 하이브리드', 2022, '기아'),  # 15.1% 오차
    ('토레스', 2022, 'KG모빌리티(쌍용)'),  # 14.6% 오차
]

for model_name, year, brand in high_error_models:
    print(f"\n{'='*70}")
    print(f"📊 {model_name} {year}년")
    print("-"*70)
    
    subset = df[(df['Model']==model_name) & (df['YearOnly']==year)]
    if len(subset) < 5:
        print(f"데이터 부족 (n={len(subset)})")
        continue
    
    print(f"데이터: {len(subset)}개")
    
    # 중앙값 샘플
    median_idx = subset['Price'].sub(subset['Price'].median()).abs().idxmin()
    sample = subset.loc[median_idx]
    
    actual = sample['Price']
    mileage = int(sample['Mileage'])
    
    # 옵션 정보 확인
    option_cols = ['has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key',
                   'has_rear_camera', 'has_led_lamp', 'has_heated_seat', 'has_ventilated_seat']
    
    print(f"\n실제 옵션:")
    options = {}
    for col in option_cols:
        if col in sample:
            val = sample[col]
            options[col] = bool(val) if pd.notna(val) else None
            status = "✅" if val == 1 else "❌" if val == 0 else "?"
            print(f"  {status} {col}: {val}")
    
    # 옵션 개수
    opt_count = sum(1 for col in option_cols if sample.get(col, 0) == 1)
    print(f"\n옵션 개수: {opt_count}/8개")
    
    # 1. 옵션 없이 예측
    base_req = {'brand': brand, 'model': model_name, 'year': year, 
                'mileage': mileage, 'fuel': '가솔린'}
    resp = requests.post(API_URL, json=base_req)
    pred_no_opt = resp.json()['predicted_price']
    error_no_opt = abs(pred_no_opt - actual) / actual * 100
    
    # 2. 실제 옵션으로 예측
    opt_req = {**base_req, **options, 'is_accident_free': True}
    resp = requests.post(API_URL, json=opt_req)
    pred_with_opt = resp.json()['predicted_price']
    error_with_opt = abs(pred_with_opt - actual) / actual * 100
    
    print(f"\n예측 결과:")
    print(f"  실제 가격:        {actual:,.0f}만원")
    print(f"  옵션 미입력:      {pred_no_opt:,.0f}만원 (오차 {error_no_opt:.1f}%)")
    print(f"  실제 옵션 입력:   {pred_with_opt:,.0f}만원 (오차 {error_with_opt:.1f}%)")
    
    improvement = error_no_opt - error_with_opt
    if improvement > 1:
        print(f"  ✅ 개선: {improvement:+.1f}% 포인트")
    elif improvement < -1:
        print(f"  ⚠️ 악화: {improvement:+.1f}% 포인트")
    else:
        print(f"  ➖ 변화 없음")

print("\n" + "="*70)
print("💡 결론")
print("="*70)
