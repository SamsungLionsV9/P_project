"""API와 동일한 로직으로 스파크 예측"""
import pandas as pd
import numpy as np
import joblib

# 입력
brand = '쉐보레'
model_name = '더 뉴 스파크'
year = 2020
mileage = 50000
fuel = '가솔린'
age = 2025 - year

# 주행거리 그룹
if mileage < 30000: mg = 'A'
elif mileage < 60000: mg = 'B'
elif mileage < 100000: mg = 'C'
elif mileage < 150000: mg = 'D'
else: mg = 'E'

# 모델/인코더/피처 로드
model = joblib.load('models/domestic_v2.pkl')
encoders = joblib.load('models/domestic_v2_encoders.pkl')
feature_cols = joblib.load('models/domestic_v2_features.pkl')

# 인코더 추출
model_enc = encoders.get('Model_enc', {})
mfr_enc = encoders.get('Manufacturer_enc', {})
my_enc = encoders.get('Model_Year_enc', {})
mym_enc = encoders.get('Model_Year_Mileage_enc', {})

# 인코딩 값 계산
default_val = 8.0
model_enc_val = model_enc.get(model_name, model_enc.get('__default__', default_val))
brand_enc_val = mfr_enc.get(brand, mfr_enc.get('__default__', default_val))
my_key = f"{model_name}_{year}"
my_enc_val = my_enc.get(my_key, model_enc_val)
mym_key = f"{model_name}_{year}_{mg}"
mym_enc_val = mym_enc.get(mym_key, my_enc_val)

print(f"인코딩 값:")
print(f"  model_enc_val: {model_enc_val:.4f} -> {np.expm1(model_enc_val):.0f}만원")
print(f"  brand_enc_val: {brand_enc_val:.4f} -> {np.expm1(brand_enc_val):.0f}만원")
print(f"  my_enc_val: {my_enc_val:.4f} -> {np.expm1(my_enc_val):.0f}만원")
print(f"  mym_enc_val: {mym_enc_val:.4f} -> {np.expm1(mym_enc_val):.0f}만원")

# 피처 생성 (API와 동일)
features = {
    'Model_enc': model_enc_val,
    'Manufacturer_enc': brand_enc_val,
    'Model_Year_enc': my_enc_val,
    'Model_Year_Mileage_enc': mym_enc_val,
    'age': age,
    'age_squared': age ** 2,
    'age_log': np.log1p(age),
    'Mileage': mileage,
    'mileage_log': np.log1p(mileage),
    'mileage_squared': mileage ** 2,
    'mileage_per_year': mileage / (age + 1),
    'option_count': 6,
    'option_rate': 0.75,
    'option_premium': 5.0,
    'has_sunroof': 0.5,
    'has_led_lamp': 0.5,
    'has_leather_seat': 0.5,
    'has_smart_key': 1,
    'is_accident_free': 1,
    'is_diesel': 0,
    'is_lpg': 0,
    'is_hybrid': 0,
    'vehicle_class': 2,
    'enc_x_age': mym_enc_val * age,
    'enc_x_mileage': mym_enc_val * np.log1p(mileage),
    'enc_x_option': mym_enc_val * 0.75
}

print(f"\n주요 피처 값:")
for k in ['Model_Year_Mileage_enc', 'age', 'enc_x_age', 'enc_x_mileage']:
    print(f"  {k}: {features[k]:.4f}")

# 예측
X = pd.DataFrame([features])[feature_cols]
log_pred = model.predict(X)[0]
pred_price = np.expm1(log_pred)

print(f"\n예측 결과:")
print(f"  log_pred: {log_pred:.4f}")
print(f"  pred_price: {pred_price:,.0f}만원")
print(f"\n실제 가격 (중앙값): 830만원")
print(f"오차: {abs(pred_price - 830) / 830 * 100:.1f}%")
