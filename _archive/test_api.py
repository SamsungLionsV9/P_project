import requests

base = {
    'brand': '현대',
    'model': '그랜저 (GN7)',
    'year': 2024,
    'mileage': 30000,
}

print("=== 연료별 가격 ===")
for fuel in ['가솔린', '디젤', '하이브리드', 'LPG']:
    r = requests.post('http://localhost:8001/api/smart-analysis', json={**base, 'fuel': fuel})
    p = r.json()['prediction']['predicted_price']
    print(f"{fuel}: {p}만원")

print("\n=== 옵션별 가격 (가솔린) ===")
r1 = requests.post('http://localhost:8001/api/smart-analysis', json={**base, 'fuel': '가솔린'})
r2 = requests.post('http://localhost:8001/api/smart-analysis', json={
    **base, 'fuel': '가솔린',
    'has_sunroof': True, 'has_navigation': True, 'has_leather_seat': True,
    'has_smart_key': True, 'has_rear_camera': True
})
p1 = r1.json()['prediction']['predicted_price']
p2 = r2.json()['prediction']['predicted_price']
print(f"옵션 없음: {p1}만원")
print(f"옵션 있음: {p2}만원 (+{p2-p1}만원)")
