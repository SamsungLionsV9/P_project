"""실제 서비스 수준 평가 - API 기반 테스트"""
import requests
import pandas as pd
import numpy as np

print("="*70)
print("🔍 실제 서비스 수준 평가")
print("="*70)

# 실제 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

# 제네시스 제외
genesis_mask = df['Manufacturer'].str.contains('제네시스|GENESIS', case=False, na=False)
df = df[~genesis_mask]
df = df[df['Price'] > 100]
df = df[df['Price'] < 12000]
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 테스트 케이스
test_cases = [
    # (모델명, 연식, 주행거리, 연료, 브랜드)
    ('더 뉴 그랜저 IG', 2022, 35000, '가솔린', '현대'),
    ('더 뉴 그랜저 IG', 2021, 50000, '가솔린', '현대'),
    ('K5 3세대', 2022, 30000, '가솔린', '기아'),
    ('K5 3세대', 2021, 45000, '가솔린', '기아'),
    ('쏘나타 (DN8)', 2022, 40000, '가솔린', '현대'),
    ('아반떼 (CN7)', 2022, 35000, '가솔린', '현대'),
    ('카니발 4세대', 2022, 40000, '디젤', '기아'),
    ('카니발 4세대', 2021, 55000, '디젤', '기아'),
    ('쏘렌토 4세대', 2022, 35000, '디젤', '기아'),
    ('팰리세이드', 2021, 50000, '디젤', '현대'),
    ('싼타페 (MX5)', 2023, 25000, '디젤', '현대'),
    ('투싼 (NX4)', 2022, 40000, '가솔린', '현대'),
    ('스포티지 5세대', 2022, 35000, '가솔린', '기아'),
    ('캐스퍼', 2023, 20000, '가솔린', '현대'),
    ('스타리아', 2022, 45000, '디젤', '현대'),
]

results = []

for model_name, year, mileage, fuel, brand in test_cases:
    # 실제 평균 가격 (유사 조건)
    mileage_range = 15000
    subset = df[(df['Model'] == model_name) & 
                (df['YearOnly'] == year) & 
                (df['Mileage'] >= mileage - mileage_range) & 
                (df['Mileage'] <= mileage + mileage_range)]
    
    if len(subset) < 3:
        continue
    
    actual_avg = subset['Price'].mean()
    actual_min = subset['Price'].min()
    actual_max = subset['Price'].max()
    
    # API 호출
    try:
        r = requests.post('http://localhost:8000/api/predict', json={
            'brand': brand,
            'model': model_name,
            'year': year,
            'mileage': mileage,
            'fuel': fuel
        }, timeout=5)
        
        if r.status_code == 200:
            data = r.json()
            predicted = data['predicted_price']
            pred_min = data['price_range'][0]
            pred_max = data['price_range'][1]
            
            error_pct = abs(predicted - actual_avg) / actual_avg * 100
            in_range = pred_min <= actual_avg <= pred_max
            
            results.append({
                'Model': model_name,
                'Year': year,
                'N': len(subset),
                'Actual_Avg': actual_avg,
                'Actual_Range': f"{actual_min:.0f}~{actual_max:.0f}",
                'Predicted': predicted,
                'Pred_Range': f"{pred_min:.0f}~{pred_max:.0f}",
                'Error%': error_pct,
                'In_Range': in_range
            })
    except:
        pass

# 결과 출력
print("\n📊 API 예측 결과 vs 실제 가격")
print("="*70)

for r in sorted(results, key=lambda x: x['Error%']):
    status = "✅" if r['Error%'] < 15 else ("⚠️" if r['Error%'] < 25 else "❌")
    range_status = "✓" if r['In_Range'] else "✗"
    print(f"{status} {r['Model']} {r['Year']}년 (n={r['N']:>2})")
    print(f"   실제: {r['Actual_Avg']:>6,.0f}만원 ({r['Actual_Range']})")
    print(f"   예측: {r['Predicted']:>6,.0f}만원 ({r['Pred_Range']}) | 오차: {r['Error%']:.1f}% | 범위포함: {range_status}")
    print()

# 요약
print("="*70)
print("📈 서비스 수준 평가 요약")
print("="*70)

if results:
    errors = [r['Error%'] for r in results]
    in_ranges = [r['In_Range'] for r in results]
    
    print(f"테스트 케이스: {len(results)}개")
    print(f"평균 오차율: {np.mean(errors):.1f}%")
    print(f"중앙값 오차율: {np.median(errors):.1f}%")
    print(f"오차 15% 이내: {len([e for e in errors if e < 15])}개 ({len([e for e in errors if e < 15])/len(errors)*100:.0f}%)")
    print(f"오차 25% 이내: {len([e for e in errors if e < 25])}개 ({len([e for e in errors if e < 25])/len(errors)*100:.0f}%)")
    print(f"범위 내 포함: {sum(in_ranges)}개 ({sum(in_ranges)/len(in_ranges)*100:.0f}%)")
    
    print("\n" + "="*70)
    print("💡 서비스 적합성 판단")
    print("="*70)
    
    avg_error = np.mean(errors)
    within_15 = len([e for e in errors if e < 15]) / len(errors) * 100
    within_25 = len([e for e in errors if e < 25]) / len(errors) * 100
    
    if avg_error < 15 and within_25 >= 90:
        print("✅ 서비스 가능 수준")
        print("   - 평균 오차 15% 미만")
        print("   - 90% 이상 케이스가 25% 오차 이내")
    elif avg_error < 20 and within_25 >= 80:
        print("⚠️ 참고용으로 사용 가능")
        print("   - '예상 가격 범위' 형태로 제공 권장")
        print("   - 정확한 시세가 아닌 참고 지표로 안내 필요")
    else:
        print("❌ 추가 개선 필요")
        print("   - 오차율이 높아 서비스 적용 어려움")
