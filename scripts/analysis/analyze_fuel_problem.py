"""
연료별 가격 문제 심층 분석
========================
LPG가 가솔린보다 비싸게 나오는 원인 파악
"""
import pandas as pd
import numpy as np

print("="*70)
print("🔍 연료별 가격 문제 심층 분석")
print("="*70)

# 데이터 로드
df = pd.read_csv('../../data/encar_raw_domestic.csv')
print(f"전체 데이터: {len(df):,}건")

# Year 형식 변환
df['YearOnly'] = (df['Year'] // 100).astype(int)

# 연료 정규화
def normalize_fuel(f):
    f = str(f).lower()
    if '하이브리드' in f or '전기' in f:
        return '하이브리드'
    elif 'lpg' in f:
        return 'LPG'
    elif '디젤' in f:
        return '디젤'
    return '가솔린'

df['Fuel'] = df['FuelType'].apply(normalize_fuel)

# ========== 1. 그랜저 연료별 분석 ==========
print("\n" + "="*70)
print("📊 1. 그랜저 연료별 실제 데이터 분석")
print("="*70)

granger = df[df['Model'].str.contains('그랜저', na=False)].copy()
granger = granger[(granger['Price'] >= 100) & (granger['Price'] <= 9000)]

print(f"\n전체 그랜저: {len(granger):,}건")

# 연료별 평균 가격
print("\n[전체 연식] 연료별 평균 가격:")
fuel_stats = granger.groupby('Fuel').agg({
    'Price': ['mean', 'median', 'count'],
    'Mileage': 'mean',
    'YearOnly': 'mean'
}).round(0)
print(fuel_stats)

# 2022년식만 분석
print("\n[2022년식만] 연료별 평균 가격:")
granger_2022 = granger[granger['YearOnly'] == 2022]
if len(granger_2022) > 0:
    fuel_2022 = granger_2022.groupby('Fuel').agg({
        'Price': ['mean', 'median', 'count'],
        'Mileage': 'mean'
    }).round(0)
    print(fuel_2022)

# ========== 2. LPG vs 가솔린 상세 비교 ==========
print("\n" + "="*70)
print("📊 2. LPG vs 가솔린 상세 비교 (2022년식)")
print("="*70)

granger_gas_2022 = granger_2022[granger_2022['Fuel'] == '가솔린']
granger_lpg_2022 = granger_2022[granger_2022['Fuel'] == 'LPG']

print(f"\n가솔린 샘플: {len(granger_gas_2022)}건")
print(f"LPG 샘플: {len(granger_lpg_2022)}건")

if len(granger_gas_2022) > 0:
    print(f"\n가솔린 평균: {granger_gas_2022['Price'].mean():.0f}만원 (중앙값: {granger_gas_2022['Price'].median():.0f})")
    print(f"가솔린 주행거리: {granger_gas_2022['Mileage'].mean()/10000:.1f}만km")
    
if len(granger_lpg_2022) > 0:
    print(f"\nLPG 평균: {granger_lpg_2022['Price'].mean():.0f}만원 (중앙값: {granger_lpg_2022['Price'].median():.0f})")
    print(f"LPG 주행거리: {granger_lpg_2022['Mileage'].mean()/10000:.1f}만km")

# ========== 3. 모델명(트림) 분석 ==========
print("\n" + "="*70)
print("📊 3. 모델명(트림) 분석 - LPG가 비싼 이유?")
print("="*70)

print("\n[가솔린 모델 분포]")
if len(granger_gas_2022) > 0:
    gas_models = granger_gas_2022['Model'].value_counts().head(10)
    for model, cnt in gas_models.items():
        avg_price = granger_gas_2022[granger_gas_2022['Model'] == model]['Price'].mean()
        print(f"  {model}: {cnt}건, 평균 {avg_price:.0f}만원")

print("\n[LPG 모델 분포]")
if len(granger_lpg_2022) > 0:
    lpg_models = granger_lpg_2022['Model'].value_counts().head(10)
    for model, cnt in lpg_models.items():
        avg_price = granger_lpg_2022[granger_lpg_2022['Model'] == model]['Price'].mean()
        print(f"  {model}: {cnt}건, 평균 {avg_price:.0f}만원")

# ========== 4. Badge(트림) 분석 ==========
print("\n" + "="*70)
print("📊 4. Badge(트림) 분석")
print("="*70)

print("\n[가솔린 트림 분포]")
if len(granger_gas_2022) > 0 and 'Badge' in granger_gas_2022.columns:
    gas_badges = granger_gas_2022.groupby('Badge')['Price'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)
    print(gas_badges)

print("\n[LPG 트림 분포]")
if len(granger_lpg_2022) > 0 and 'Badge' in granger_lpg_2022.columns:
    lpg_badges = granger_lpg_2022.groupby('Badge')['Price'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)
    print(lpg_badges)

# ========== 5. 동일 모델명 비교 ==========
print("\n" + "="*70)
print("📊 5. 동일 모델명 내 연료별 가격 비교")
print("="*70)

# 더 뉴 그랜저 IG만 비교
ig_gas = granger[(granger['Model'] == '더 뉴 그랜저 IG') & (granger['Fuel'] == '가솔린') & (granger['YearOnly'] == 2022)]
ig_lpg = granger[(granger['Model'] == '더 뉴 그랜저 IG') & (granger['Fuel'] == 'LPG') & (granger['YearOnly'] == 2022)]

print(f"\n더 뉴 그랜저 IG (2022년식):")
print(f"  가솔린: {len(ig_gas)}건, 평균 {ig_gas['Price'].mean():.0f}만원" if len(ig_gas) > 0 else "  가솔린: 데이터 없음")
print(f"  LPG: {len(ig_lpg)}건, 평균 {ig_lpg['Price'].mean():.0f}만원" if len(ig_lpg) > 0 else "  LPG: 데이터 없음")

# ========== 6. 전체 연료별 샘플 수 ==========
print("\n" + "="*70)
print("📊 6. 전체 데이터 연료별 샘플 수")
print("="*70)

fuel_total = df.groupby('Fuel').size()
print(fuel_total)
print(f"\nLPG 비율: {fuel_total.get('LPG', 0) / len(df) * 100:.1f}%")

# ========== 7. 문제 원인 요약 ==========
print("\n" + "="*70)
print("🎯 7. 문제 원인 분석 결과")
print("="*70)

print("""
가능한 원인:
1. [트림 차이] LPG는 주로 고급 트림(프리미엄, 익스클루시브)에 많이 적용됨
2. [배기량 차이] LPG 3.0L vs 가솔린 2.5L
3. [샘플 불균형] LPG 샘플이 적어서 고가 차량이 평균을 올림
4. [택시/렌트 제외] 저가 택시용 LPG가 데이터에서 제외되었을 수 있음

해결 방안:
1. 동일 트림끼리만 비교하도록 트림 피처 추가
2. 배기량 피처 추가
3. 연료별 가격 조정 로직 수동 추가 (시장 현실 반영)
""")
