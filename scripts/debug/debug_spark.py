"""스파크 디버깅"""
import pandas as pd
import numpy as np
import joblib

# 입력 데이터 (API와 동일)
brand = '쉐보레'
model_name = '더 뉴 스파크'
year = 2020
mileage = 50000
fuel = '가솔린'

# 주행거리 그룹
if mileage < 30000: mg = 'A'
elif mileage < 60000: mg = 'B'
elif mileage < 100000: mg = 'C'
elif mileage < 150000: mg = 'D'
else: mg = 'E'

print(f"입력: {model_name} {year}년 {mileage}km")
print(f"주행거리 그룹: {mg}")

# 인코더 로드
encoders = joblib.load('models/domestic_v2_encoders.pkl')
mym_enc = encoders.get('Model_Year_Mileage_enc', {})
my_enc = encoders.get('Model_Year_enc', {})
model_enc = encoders.get('Model_enc', {})

# 키 생성
mym_key = f"{model_name}_{year}_{mg}"
my_key = f"{model_name}_{year}"

print(f"\n생성된 키:")
print(f"  Model_Year_Mileage: '{mym_key}'")
print(f"  Model_Year: '{my_key}'")

# 인코더에서 조회
print(f"\n인코더 조회 결과:")
mym_val = mym_enc.get(mym_key, None)
my_val = my_enc.get(my_key, None)
model_val = model_enc.get(model_name, None)

print(f"  Model_Year_Mileage_enc: {mym_val} -> {np.expm1(mym_val) if mym_val else 'None'}만원")
print(f"  Model_Year_enc: {my_val} -> {np.expm1(my_val) if my_val else 'None'}만원")
print(f"  Model_enc: {model_val} -> {np.expm1(model_val) if model_val else 'None'}만원")

# 인코더에 있는 실제 키 확인
print(f"\n인코더에 있는 비슷한 키:")
similar_keys = [k for k in mym_enc.keys() if '스파크' in k and '2020' in k]
for k in similar_keys:
    print(f"  '{k}': {np.expm1(mym_enc[k]):.0f}만원")

# 키 비교
if similar_keys:
    print(f"\n키 비교:")
    print(f"  생성된 키: '{mym_key}' (len={len(mym_key)})")
    print(f"  실제 키:   '{similar_keys[0]}' (len={len(similar_keys[0])})")
    print(f"  동일 여부: {mym_key == similar_keys[0]}")
    
    # 바이트 비교
    print(f"\n바이트 비교:")
    for i, (a, b) in enumerate(zip(mym_key, similar_keys[0])):
        if a != b:
            print(f"  위치 {i}: '{a}' vs '{b}'")
