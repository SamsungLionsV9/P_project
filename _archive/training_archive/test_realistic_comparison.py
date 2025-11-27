"""
현실적인 시나리오 테스트:
- 아반떼 2023년 풀옵션 1만km vs 소나타 2020년 노옵션 10만km
- 이 경우 아반떼가 더 비싸야 정상!
"""
import requests
import pandas as pd
import numpy as np

API_URL = "http://localhost:8000/api/predict"

print("="*70)
print("🔍 현실적인 시나리오 테스트")
print("="*70)

def predict(brand, model, year, mileage, options=None):
    data = {
        'brand': brand, 'model': model, 'year': year,
        'mileage': mileage, 'fuel': '가솔린'
    }
    if options:
        data.update(options)
    resp = requests.post(API_URL, json=data)
    return resp.json()['predicted_price']

# ============================================================
print("\n" + "="*70)
print("📊 시나리오 1: 아반떼 최신+풀옵 vs 소나타 구형+노옵")
print("="*70)

# 아반떼: 최신 연식, 저주행, 풀옵션
avante_new = predict('현대', '아반떼 (CN7)', 2023, 10000, {
    'has_sunroof': True, 'has_leather_seat': True, 'has_smart_key': True,
    'has_navigation': True, 'has_rear_camera': True, 'has_led_lamp': True,
    'has_heated_seat': True, 'has_ventilated_seat': True
})

# 소나타: 구형 연식, 고주행, 노옵션
sonata_old = predict('현대', '쏘나타 (DN8)', 2020, 100000, {
    'has_sunroof': False, 'has_leather_seat': False, 'has_smart_key': False,
    'has_navigation': False, 'has_rear_camera': False, 'has_led_lamp': False,
    'has_heated_seat': False, 'has_ventilated_seat': False
})

print(f"\n아반떼 2023년 1만km 풀옵션: {avante_new:,.0f}만원")
print(f"소나타 2020년 10만km 노옵션: {sonata_old:,.0f}만원")

if avante_new > sonata_old:
    print(f"\n✅ 정상! 아반떼가 {avante_new - sonata_old:,.0f}만원 더 비쌈")
else:
    print(f"\n⚠️ 이상! 소나타가 {sonata_old - avante_new:,.0f}만원 더 비쌈")

# ============================================================
print("\n" + "="*70)
print("📊 시나리오 2: 동일 조건에서의 모델 서열")
print("="*70)

print("\n[조건: 2022년 3만km 기본옵션]")
models = [
    ('현대', '아반떼 (CN7)', '준중형'),
    ('현대', '쏘나타 (DN8)', '중형'),
    ('현대', '더 뉴 그랜저 IG', '대형'),
]

default_options = {
    'has_sunroof': False, 'has_leather_seat': False, 'has_smart_key': True,
    'has_navigation': True, 'has_rear_camera': True, 'has_led_lamp': False,
}

for brand, model, seg in models:
    price = predict(brand, model, 2022, 30000, default_options)
    print(f"  {seg:6} {model:20}: {price:,.0f}만원")

# ============================================================
print("\n" + "="*70)
print("📊 시나리오 3: 옵션이 가격에 미치는 영향")
print("="*70)

print("\n[그랜저 2022년 3만km - 옵션별 가격]")

# 노옵션
no_opt = predict('현대', '더 뉴 그랜저 IG', 2022, 30000, {
    'has_sunroof': False, 'has_leather_seat': False, 'has_smart_key': False,
    'has_navigation': False, 'has_rear_camera': False, 'has_led_lamp': False,
    'has_heated_seat': False, 'has_ventilated_seat': False
})

# 풀옵션
full_opt = predict('현대', '더 뉴 그랜저 IG', 2022, 30000, {
    'has_sunroof': True, 'has_leather_seat': True, 'has_smart_key': True,
    'has_navigation': True, 'has_rear_camera': True, 'has_led_lamp': True,
    'has_heated_seat': True, 'has_ventilated_seat': True
})

print(f"  노옵션:  {no_opt:,.0f}만원")
print(f"  풀옵션:  {full_opt:,.0f}만원")
print(f"  옵션 차이: {full_opt - no_opt:,.0f}만원 ({(full_opt-no_opt)/no_opt*100:.1f}%)")

# ============================================================
print("\n" + "="*70)
print("📊 시나리오 4: 연식+주행거리+옵션 복합 영향")
print("="*70)

scenarios = [
    ("아반떼 2024년 5천km 풀옵", '현대', '아반떼 (CN7)', 2024, 5000, True),
    ("소나타 2022년 3만km 중간", '현대', '쏘나타 (DN8)', 2022, 30000, None),
    ("그랜저 2020년 8만km 노옵", '현대', '더 뉴 그랜저 IG', 2020, 80000, False),
    ("G80 2019년 12만km 노옵", '제네시스', 'G80 (RG3)', 2019, 120000, False),
]

print("\n복합 시나리오 비교:")
for name, brand, model, year, mileage, full in scenarios:
    if full is True:
        opts = {'has_sunroof': True, 'has_leather_seat': True, 'has_smart_key': True,
                'has_led_lamp': True, 'has_navigation': True}
    elif full is False:
        opts = {'has_sunroof': False, 'has_leather_seat': False, 'has_smart_key': False,
                'has_led_lamp': False, 'has_navigation': False}
    else:
        opts = {}
    
    price = predict(brand, model, year, mileage, opts)
    print(f"  {name:30}: {price:,.0f}만원")

# ============================================================
print("\n" + "="*70)
print("💡 결론")
print("="*70)
print("""
✅ 모델이 고려하는 것들:
   1. 모델(차급) - Model_Year_Mileage Target Encoding
   2. 연식 - 최신일수록 가격 ↑
   3. 주행거리 - 적을수록 가격 ↑
   4. 옵션 - 풀옵션일수록 가격 ↑

⚠️ "아반떼가 소나타보다 비쌀 수 있다"
   → 이건 오류가 아님!
   → 아반떼 2023년 풀옵 1만km가 소나타 2020년 노옵 10만km보다 비싼 건 정상

✅ 서열이 유지되어야 하는 조건:
   "동일 연식, 동일 주행거리, 동일 옵션"일 때만
   아반떼 < 소나타 < 그랜저 서열이 유지되어야 함
""")
