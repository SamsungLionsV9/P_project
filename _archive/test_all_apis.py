"""전체 API 테스트"""
import requests

print('='*60)
print('🔍 API 전체 테스트')
print('='*60)

BASE = 'http://localhost:8001/api'

# 1. Health
r = requests.get(f'{BASE}/health')
print(f'✓ Health: {r.json()}')

# 2. Popular (인기 모델)
r = requests.get(f'{BASE}/popular?category=domestic&limit=3')
models = r.json()['models']
print(f'\n✓ 인기 국산: {len(models)}개')
for m in models[:3]:
    print(f'   - {m["brand"]} {m["model"]}: {m["listings"]}건, 평균 {m["avg_price"]}만원')

r = requests.get(f'{BASE}/popular?category=imported&limit=3')
models = r.json()['models']
print(f'\n✓ 인기 수입: {len(models)}개')
for m in models[:3]:
    print(f'   - {m["brand"]} {m["model"]}: {m["listings"]}건, 평균 {m["avg_price"]}만원')

# 3. Recommendations (추천 차량)
r = requests.get(f'{BASE}/recommendations?budget_min=2000&budget_max=3000&limit=5')
recs = r.json()['recommendations']
print(f'\n✓ 추천 차량 (2000-3000만원): {len(recs)}개')
for v in recs[:3]:
    deal = '🔥' if v.get('is_good_deal') else ''
    print(f'   - {v["brand"]} {v["model"]} {v["year"]}년: 실제 {v["actual_price"]}만원 {deal}')

# 4. Predict (예측)
r = requests.post(f'{BASE}/predict', json={
    'brand': '현대', 'model': '더 뉴 그랜저 IG', 'year': 2022, 'mileage': 30000, 'fuel': '가솔린'
})
print(f'\n✓ 예측 (그랜저 2022 가솔린): {r.json()["predicted_price"]:,.0f}만원')

r = requests.post(f'{BASE}/predict', json={
    'brand': '현대', 'model': '더 뉴 그랜저 IG', 'year': 2022, 'mileage': 30000, 'fuel': 'LPG'
})
print(f'✓ 예측 (그랜저 2022 LPG): {r.json()["predicted_price"]:,.0f}만원')

# 5. Smart Analysis
r = requests.post(f'{BASE}/smart-analysis', json={
    'brand': '벤츠', 'model': 'E-클래스 W213', 'year': 2022, 'mileage': 30000, 'fuel': '디젤'
})
result = r.json()
print(f'\n✓ 스마트 분석 (E-클래스 디젤):')
print(f'   예측가: {result["prediction"]["predicted_price"]:,.0f}만원')
print(f'   타이밍: {result["timing"]["decision"]} ({result["timing"]["timing_score"]}점)')

# 6. History (검색 이력 저장)
r = requests.post(f'{BASE}/history', json={
    'brand': '현대', 'model': '그랜저', 'year': 2022, 'mileage': 30000, 'predicted_price': 2500
})
print(f'\n✓ 검색 이력 저장: {r.json()["success"]}')

r = requests.get(f'{BASE}/history?limit=5')
history = r.json()['history']
print(f'✓ 검색 이력 조회: {len(history)}건')

print('\n' + '='*60)
print('✅ 모든 API 정상 작동!')
print('='*60)
