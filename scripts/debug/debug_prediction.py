"""국산차 모델 예측 디버깅"""
import pandas as pd
import numpy as np
import joblib

# 모델 로드
model = joblib.load('models/domestic_ultimate.pkl')
encoders = joblib.load('models/domestic_ultimate_encoders.pkl')
feature_cols = joblib.load('models/domestic_ultimate_features.pkl')

# 인코더 변환
model_enc = encoders['Model_target_enc']
if hasattr(model_enc, 'to_dict'):
    model_enc = model_enc.to_dict()
    
mfr_enc = encoders['Manufacturer_target_enc']
if hasattr(mfr_enc, 'to_dict'):
    mfr_enc = mfr_enc.to_dict()

print("=== 그랜저 2022년식 35000km 예측 ===")
print(f"Model Target Enc (그랜저): {model_enc.get('그랜저', 'NOT FOUND')}")
print(f"Manufacturer Target Enc (현대): {mfr_enc.get('현대', 'NOT FOUND')}")

# 옵션 기본값 (실제 평균 장착률)
option_defaults = {
    'has_sunroof': 0.42, 'has_navigation': 0.89, 'has_leather_seat': 0.67,
    'has_smart_key': 0.85, 'has_rear_camera': 0.78, 'has_led_lamp': 0.54,
    'has_parking_sensor': 0.61, 'has_auto_ac': 0.73,
    'has_heated_seat': 0.69, 'has_ventilated_seat': 0.38
}

# 피처 생성
year = 2022
mileage = 35000
age = 2025 - year  # = 3

model_target = model_enc.get('그랜저', 7.5)
mfr_target = mfr_enc.get('현대', 7.5)

option_score = sum(option_defaults.values())
option_rate = option_score / 10.0
option_weighted = option_score * 1.2

# price_segment 계산 (새로운 방식)
base_price = np.expm1(model_target)  # 모델 평균 가격
age_factor = 1.0 + (5 - age) * 0.12 if age <= 5 else 1.0 - (age - 5) * 0.08
age_factor = max(0.5, min(1.8, age_factor))
mileage_factor = 1.0 - (mileage / 100000) * 0.15
mileage_factor = max(0.7, min(1.1, mileage_factor))
estimated_price = base_price * age_factor * mileage_factor

segment_boundaries = [0, 490, 690, 900, 1180, 1470, 1770, 2190, 2750, 3630, 999999]
price_segment = 9
for i, bound in enumerate(segment_boundaries[1:]):
    if estimated_price < bound:
        price_segment = i
        break

print(f"\nage: {age}")
print(f"base_price (exp(model_enc)-1): {base_price:.0f}만원")
print(f"age_factor: {age_factor:.3f}")
print(f"mileage_factor: {mileage_factor:.3f}")
print(f"estimated_price: {estimated_price:.0f}만원")
print(f"price_segment: {price_segment}")
print(f"option_score: {option_score:.2f}")

# 데이터프레임 생성
df = pd.DataFrame({
    'Year': [year], 'age': [age], 'age_squared': [age**2], 'age_cubed': [age**3],
    'Mileage': [mileage], 'mileage_log': [np.log1p(mileage)], 
    'mileage_squared': [mileage**2], 'mileage_per_year': [mileage/(age+1)],
    'Model_target_enc': [model_target], 'Manufacturer_target_enc': [mfr_target],
    'FuelType_encoded': [0], 'mileage_condition_encoded': [1], 'price_segment': [price_segment],
    'is_eco_fuel': [0], 'is_accident_free': [1], 'inspection_score': [2], 'is_premium_condition': [0],
    **{col: [val] for col, val in option_defaults.items()},
    'option_score': [option_score], 'option_rate': [option_rate], 'option_weighted': [option_weighted],
    'is_metro': [1], 
    'age_option_interaction': [age * option_rate],
    'age_mileage_interaction': [age * np.log1p(mileage)],
    'model_option_interaction': [model_target * option_weighted]
})

# 피처 값 출력
print("\n=== Feature Values ===")
X = df[feature_cols]
for col in feature_cols:
    print(f"{col}: {X[col].values[0]:.4f}")

# 예측
pred_log = model.predict(X)[0]
pred_price = np.expm1(pred_log)
print(f"\n=== 예측 결과 ===")
print(f"Predicted log: {pred_log:.4f}")
print(f"Predicted price: {pred_price:,.0f}만원")
print(f"실제 2022년 그랜저 평균: ~2,832만원")
