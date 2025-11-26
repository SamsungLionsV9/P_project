"""국산차 데이터 심층 분석"""
import pandas as pd
import numpy as np

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')

# 제네시스 제외
genesis_keywords = ['제네시스', 'GENESIS', 'Genesis']
genesis_mask = df['Manufacturer'].str.contains('|'.join(genesis_keywords), case=False, na=False)
df = df[~genesis_mask]

# 전처리
df = df.dropna(subset=['Price', 'Mileage', 'Year', 'Manufacturer', 'Model'])
df = df[df['Price'] > 100]
df = df[df['Price'] < 12000]
df['YearOnly'] = (df['Year']//100).astype(int)
df['age'] = 2025 - df['YearOnly']
df['Price_log'] = np.log1p(df['Price'])

print("="*60)
print("📊 국산차 데이터 분석")
print("="*60)

# 1. 기본 통계
print(f"\n총 데이터: {len(df):,}행")
print(f"가격 범위: {df['Price'].min():.0f} ~ {df['Price'].max():.0f}만원")
print(f"가격 평균: {df['Price'].mean():,.0f}만원")
print(f"가격 중앙값: {df['Price'].median():,.0f}만원")

# 2. 제조사별 분포
print("\n=== 제조사별 분포 ===")
mfr_stats = df.groupby('Manufacturer').agg({
    'Price': ['count', 'mean', 'std'],
    'age': 'mean'
}).round(0)
mfr_stats.columns = ['count', 'avg_price', 'std_price', 'avg_age']
print(mfr_stats.sort_values('count', ascending=False).head(10))

# 3. 모델별 가격 분포 (상위 20개)
print("\n=== 인기 모델별 가격 (상위 20개) ===")
model_stats = df.groupby('Model').agg({
    'Price': ['count', 'mean', 'std', 'min', 'max'],
    'age': 'mean'
}).round(0)
model_stats.columns = ['count', 'avg_price', 'std_price', 'min_price', 'max_price', 'avg_age']
model_stats = model_stats[model_stats['count'] >= 100].sort_values('count', ascending=False)
print(model_stats.head(20))

# 4. 연식별 가격 분포
print("\n=== 연식별 평균 가격 ===")
year_stats = df.groupby('YearOnly').agg({
    'Price': ['count', 'mean'],
}).round(0)
year_stats.columns = ['count', 'avg_price']
print(year_stats.tail(10))

# 5. 가격과 주요 변수 간 상관관계
print("\n=== 가격과의 상관관계 ===")
numeric_cols = ['Price', 'Mileage', 'age', 'is_accident_free']
option_cols = ['has_sunroof', 'has_navigation', 'has_leather_seat', 'has_smart_key',
               'has_rear_camera', 'has_led_lamp', 'has_parking_sensor']
for col in option_cols:
    if col in df.columns:
        numeric_cols.append(col)

corr = df[numeric_cols].corr()['Price'].sort_values(ascending=False)
print(corr)

# 6. 차급 추정 (모델명 기반)
print("\n=== 차급별 분포 추정 ===")
def classify_segment(model):
    model_lower = str(model).lower()
    # SUV
    if any(x in model_lower for x in ['투싼', '코나', '싼타페', '팰리세이드', 'suv', '쏘렌토', '스포티지', '셀토스', 'ex', 'gv']):
        return 'SUV'
    # 대형
    elif any(x in model_lower for x in ['그랜저', 'k7', 'k8', 'k9', 'g80', 'g90', 'eq']):
        return '대형'
    # 중형
    elif any(x in model_lower for x in ['쏘나타', 'k5', '옵티마', '아슬란']):
        return '중형'
    # 준중형
    elif any(x in model_lower for x in ['아반떼', 'k3', '포르테', '엘란트라']):
        return '준중형'
    # 소형/경차
    elif any(x in model_lower for x in ['모닝', '레이', '캐스퍼', '스파크', '액센트', '베르나']):
        return '소형/경차'
    # MPV/밴
    elif any(x in model_lower for x in ['카니발', '스타리아', '스타렉스', '포터', '봉고']):
        return 'MPV/밴'
    else:
        return '기타'

df['segment'] = df['Model'].apply(classify_segment)
segment_stats = df.groupby('segment').agg({
    'Price': ['count', 'mean', 'std']
}).round(0)
segment_stats.columns = ['count', 'avg_price', 'std_price']
print(segment_stats.sort_values('avg_price', ascending=False))

# 7. 연식별 감가율 분석
print("\n=== 모델별 연식 감가율 (그랜저 예시) ===")
granger = df[df['Model'].str.contains('그랜저', na=False)]
granger_by_year = granger.groupby('YearOnly')['Price'].mean()
print(granger_by_year.tail(7))

# 8. 결론
print("\n" + "="*60)
print("💡 분석 결론")
print("="*60)
print("1. 차급(segment)이 가격에 큰 영향")
print("2. 연식에 따른 감가율이 모델마다 다름")
print("3. 옵션 유무보다 모델 자체가 더 중요")
print("4. 주행거리와 가격은 약한 음의 상관관계")
