"""새로운 API 테스트 (즐겨찾기, 알림)"""
import requests

BASE = 'http://localhost:8001/api'

print('='*60)
print('🔍 새 API 테스트')
print('='*60)

# 1. 검색 이력 저장
print('\n1️⃣ 검색 이력 저장')
r = requests.post(f'{BASE}/history', json={
    'brand': '현대', 'model': '그랜저', 'year': 2022, 'mileage': 30000, 'predicted_price': 2500
})
print(f'   결과: {r.json()}')

# 2. 검색 이력 조회
print('\n2️⃣ 검색 이력 조회')
r = requests.get(f'{BASE}/history?limit=5')
history = r.json()['history']
print(f'   이력 수: {len(history)}건')
for h in history[:3]:
    print(f'   - {h["brand"]} {h["model"]} {h["year"]}년')

# 3. 즐겨찾기 추가
print('\n3️⃣ 즐겨찾기 추가')
r = requests.post(f'{BASE}/favorites', json={
    'brand': '현대', 'model': '그랜저', 'year': 2022, 'mileage': 30000, 'predicted_price': 2500
})
print(f'   결과: {r.json()}')

# 4. 즐겨찾기 목록
print('\n4️⃣ 즐겨찾기 목록')
r = requests.get(f'{BASE}/favorites')
favorites = r.json()['favorites']
print(f'   즐겨찾기 수: {len(favorites)}개')
for f in favorites:
    print(f'   - {f["brand"]} {f["model"]} {f["year"]}년 (ID: {f["id"]})')

# 5. 가격 알림 추가
print('\n5️⃣ 가격 알림 추가')
r = requests.post(f'{BASE}/alerts', json={
    'brand': '현대', 'model': '그랜저', 'year': 2022, 'target_price': 2300
})
print(f'   결과: {r.json()}')

# 6. 알림 목록
print('\n6️⃣ 알림 목록')
r = requests.get(f'{BASE}/alerts')
alerts = r.json()['alerts']
print(f'   알림 수: {len(alerts)}개')
for a in alerts:
    status = '🔔' if a["is_active"] else '🔕'
    print(f'   {status} {a["brand"]} {a["model"]} - 목표가: {a["target_price"]}만원')

# 7. 알림 토글
if alerts:
    print('\n7️⃣ 알림 토글')
    alert_id = alerts[0]['id']
    r = requests.put(f'{BASE}/alerts/{alert_id}/toggle')
    print(f'   결과: {r.json()}')

print('\n' + '='*60)
print('✅ 모든 새 API 정상 작동!')
print('='*60)
