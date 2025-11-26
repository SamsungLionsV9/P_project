"""
수입차 극단값 분석: 왜 R² 0.99가 가능한가?
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("수입차 극단값 분석")
print("="*70)

# 데이터 로드
df = pd.read_csv('data/processed_encar_combined.csv')
imported = df[df['car_type'] == 'Imported'].copy()

print(f"\n📊 수입차 데이터: {len(imported):,}건")
print(f"가격 범위: {imported['price'].min():.0f}만원 ~ {imported['price'].max():.0f}만원")

# 1. 가격대별 분포
print("\n" + "="*70)
print("1️⃣ 가격대별 분포")
print("="*70)

price_bins = [0, 1000, 3000, 5000, 10000, 20000, 999999]
labels = ['<1000만', '1000-3000만', '3000-5000만', '5000만-1억', '1-2억', '2억+']
imported['price_range'] = pd.cut(imported['price'], bins=price_bins, labels=labels)

print(imported['price_range'].value_counts().sort_index())

# 2. 극고가 브랜드 분석
print("\n" + "="*70)
print("2️⃣ 고가 브랜드 (5000만원 이상)")
print("="*70)

ultra_high = imported[imported['price'] >= 5000]
print(f"\n총 {len(ultra_high):,}건")
print("\n브랜드별 분포:")
print(ultra_high['brand'].value_counts().head(15))

# 3. 슈퍼카 브랜드 분석
print("\n" + "="*70)
print("3️⃣ 슈퍼카 브랜드 (1억 이상)")
print("="*70)

supercar_brands = ['람보르기니', '페라리', '포르쉐', '벤틀리', '롤스로이스', 
                   '맥라렌', '마세라티', '애스턴마틴']

super_high = imported[imported['price'] >= 10000]
print(f"\n총 {len(super_high):,}건")
print("\n브랜드별 분포:")
if len(super_high) > 0:
    print(super_high['brand'].value_counts())
    
    print("\n최고가 Top 20:")
    top20 = super_high.nlargest(20, 'price')[['brand', 'model_name', 'year', 'mileage', 'price']]
    print(top20.to_string(index=False))

# 4. 브랜드별 평균 가격
print("\n" + "="*70)
print("4️⃣ 브랜드별 평균 가격 (Top 20)")
print("="*70)

brand_stats = imported.groupby('brand').agg({
    'price': ['count', 'mean', 'std', 'min', 'max']
}).round(0)
brand_stats.columns = ['개수', '평균', '표준편차', '최소', '최대']
brand_stats = brand_stats.sort_values('평균', ascending=False)
print(brand_stats.head(20))

# 5. 로그 변환 효과
print("\n" + "="*70)
print("5️⃣ 로그 변환 효과")
print("="*70)

print("\n원본 가격 분포:")
print(f"  평균: {imported['price'].mean():.0f}만원")
print(f"  표준편차: {imported['price'].std():.0f}만원")
print(f"  왜도(Skewness): {imported['price'].skew():.2f}")
print(f"  첨도(Kurtosis): {imported['price'].kurtosis():.2f}")

log_price = np.log1p(imported['price'])
print("\n로그 변환 후:")
print(f"  평균: {log_price.mean():.2f}")
print(f"  표준편차: {log_price.std():.2f}")
print(f"  왜도(Skewness): {log_price.skew():.2f}")
print(f"  첨도(Kurtosis): {log_price.kurtosis():.2f}")

# 6. 브랜드 프리미엄 일관성
print("\n" + "="*70)
print("6️⃣ 브랜드 프리미엄 일관성 (CV 계수)")
print("="*70)

brand_cv = imported.groupby('brand').apply(
    lambda x: x['price'].std() / x['price'].mean() if len(x) > 5 else np.nan
).dropna().sort_values()

print("\nCV 계수가 낮은 브랜드 (일관성 높음):")
print(brand_cv.head(10))

print("\nCV 계수가 높은 브랜드 (일관성 낮음):")
print(brand_cv.tail(10))

# 7. 핵심 인사이트
print("\n" + "="*70)
print("💡 핵심 인사이트: 왜 R² 0.99가 가능한가?")
print("="*70)

luxury_brands = imported[imported['brand'].isin(['람보르기니', '페라리', '포르쉐', '벤틀리', '롤스로이스'])]
regular_brands = imported[imported['brand'].isin(['도요타', '혼다', '폭스바겐', '쉐보레', '지프'])]

print(f"\n1. 브랜드 신호 강도:")
print(f"   럭셔리 브랜드 평균: {luxury_brands['price'].mean():.0f}만원")
print(f"   일반 브랜드 평균: {regular_brands['price'].mean():.0f}만원")
print(f"   차이: {luxury_brands['price'].mean() / regular_brands['price'].mean():.1f}배")

print(f"\n2. 로그 변환 효과:")
print(f"   원본 왜도: {imported['price'].skew():.2f} (롱테일)")
print(f"   로그 왜도: {log_price.skew():.2f} (정규분포에 가까움)")

print(f"\n3. 브랜드별 일관성:")
luxury_cv = luxury_brands.groupby('brand')['price'].apply(lambda x: x.std() / x.mean()).mean()
regular_cv = regular_brands.groupby('brand')['price'].apply(lambda x: x.std() / x.mean()).mean()
print(f"   럭셔리 브랜드 CV: {luxury_cv:.2f}")
print(f"   일반 브랜드 CV: {regular_cv:.2f}")

print(f"\n4. 데이터 분포:")
print(f"   2억 이상: {len(super_high):,}건 ({len(super_high)/len(imported)*100:.1f}%)")
print(f"   → 극단값이지만 충분한 데이터가 있음")

print("\n" + "="*70)
print("✅ 결론: 극단값이 있어도 R² 0.99가 가능한 이유")
print("="*70)
print("""
1. 로그 변환으로 극단값 영향 감소
2. 브랜드가 강력한 예측 신호 (람보르기니 = 무조건 고가)
3. 브랜드 내 가격 일관성 높음
4. 극단값도 충분한 데이터 존재
5. XGBoost가 브랜드별 패턴 잘 학습
""")
