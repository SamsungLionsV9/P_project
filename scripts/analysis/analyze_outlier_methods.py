"""현재 이상치 처리 방법 분석 및 추가 개선점 도출"""
import pandas as pd
import numpy as np
from scipy import stats

print("="*80)
print("🔍 현재 이상치 처리 방법 분석 & 추가 개선점")
print("="*80)

# 데이터 로드
df_raw = pd.read_csv('encar_raw_domestic.csv')
df_detail = pd.read_csv('data/complete_domestic_details.csv')
df = df_raw.merge(df_detail, left_on='Id', right_on='car_id', how='inner')
df['YearOnly'] = (df['Year'] // 100).astype(int)
df['age'] = 2025 - df['YearOnly']

print(f"\n원본 데이터: {len(df):,}행")

# ============================================================
print("\n" + "="*80)
print("📋 현재 시행 중인 이상치 처리 방법")
print("="*80)

methods = [
    ("1. 중복 데이터 제거", "Model+Year+Mileage+Price 동일한 중복 제거"),
    ("2. 패턴 가격 이상치", "1111, 2222, 7777, 9999 등 특수 숫자"),
    ("3. 연간 주행거리 이상치", "연 4만km 초과 또는 연 2천km 미만"),
    ("4. 모델+연식별 3σ 이상치", "그룹 내 Z-score ±3 초과"),
]

for method, desc in methods:
    print(f"  ✅ {method}: {desc}")

# ============================================================
print("\n" + "="*80)
print("🔍 추가 가능한 이상치 처리 방법 분석")
print("="*80)

# 1. IQR 방식 vs 3σ 방식 비교
print("\n1️⃣ IQR 1.5배 vs 3σ 비교")
print("-"*60)

# 그랜저 IG 2022년 예시
granger = df[(df['Model']=='더 뉴 그랜저 IG') & (df['YearOnly']==2022)]
q1, q3 = granger['Price'].quantile([0.25, 0.75])
iqr = q3 - q1
iqr_lower = q1 - 1.5 * iqr
iqr_upper = q3 + 1.5 * iqr

mean = granger['Price'].mean()
std = granger['Price'].std()
sigma_lower = mean - 3 * std
sigma_upper = mean + 3 * std

print(f"  그랜저 IG 2022년 (n={len(granger)})")
print(f"  IQR 방식: {iqr_lower:,.0f} ~ {iqr_upper:,.0f}만원")
print(f"  3σ 방식: {sigma_lower:,.0f} ~ {sigma_upper:,.0f}만원")
print(f"  → IQR이 더 엄격함 (좁은 범위)")

# 2. 주행거리 대비 가격 이상치
print("\n2️⃣ 주행거리 대비 가격 이상치 (미구현)")
print("-"*60)

# 같은 모델+연식 내에서 주행거리 높은데 가격 높은 케이스
def find_mileage_price_anomaly(group):
    if len(group) < 10:
        return None
    corr = group['Mileage'].corr(group['Price'])
    return corr

anomalies = df.groupby(['Model', 'YearOnly']).apply(find_mileage_price_anomaly, include_groups=False)
anomalies = anomalies.dropna()

# 양의 상관관계 (주행거리 높을수록 비싼 이상한 케이스)
positive_corr = anomalies[anomalies > 0.3]
print(f"  주행거리↑ 가격↑ 이상 그룹: {len(positive_corr)}개")
if len(positive_corr) > 0:
    print(f"  예시: {positive_corr.head(3).index.tolist()}")

# 3. 허위 매물 (신차 대비 과도한 감가)
print("\n3️⃣ 허위 매물 의심 (신차 대비 과도한 감가)")
print("-"*60)

# 연식 1~2년 차인데 가격이 그룹 평균의 50% 미만
recent = df[(df['age'] <= 2) & (df['Price'] > 0)]
recent_stats = recent.groupby('Model')['Price'].agg(['mean', 'median'])
recent = recent.merge(recent_stats, on='Model', suffixes=('', '_avg'))
suspicious = recent[recent['Price'] < recent['mean'] * 0.5]
print(f"  최신 연식(1~2년) + 평균 50% 미만: {len(suspicious)}건")
if len(suspicious) > 0:
    print(f"  예시:")
    for _, row in suspicious.head(3).iterrows():
        print(f"    - {row['Model']} {row['YearOnly']}년: {row['Price']:,.0f}만원 (평균 {row['mean']:,.0f})")

# 4. 가격 단위 오류
print("\n4️⃣ 가격 단위 오류 (미구현)")
print("-"*60)

# 극단적으로 높거나 낮은 가격
extreme_low = df[df['Price'] < 50]  # 50만원 미만
extreme_high = df[df['Price'] > 50000]  # 5억 초과
print(f"  가격 < 50만원: {len(extreme_low)}건")
print(f"  가격 > 5억원: {len(extreme_high)}건")

# Log 변환 후 분포 확인
df['Price_log'] = np.log1p(df['Price'])
z_scores = np.abs(stats.zscore(df['Price_log']))
log_outliers = df[z_scores > 3]
print(f"  Log 변환 후 Z-score > 3: {len(log_outliers)}건")

# 5. 특수 목적 차량 (렌터카 등)
print("\n5️⃣ 특수 목적 차량")
print("-"*60)

# 용도 컬럼 확인
if 'usage' in df.columns or 'UsageHistory' in df.columns:
    usage_col = 'usage' if 'usage' in df.columns else 'UsageHistory'
    print(f"  용도 컬럼: {usage_col}")
    print(df[usage_col].value_counts().head())
else:
    print("  ⚠️ 용도 이력 컬럼 없음")
    
# 렌터카/리스 관련 텍스트 검색
if 'car_description' in df.columns:
    rental = df[df['car_description'].str.contains('렌터카|리스|법인', na=False, regex=True)]
    print(f"  설명에 '렌터카/리스/법인' 포함: {len(rental)}건")

# 6. 사고 차량
print("\n6️⃣ 사고 차량")
print("-"*60)

if 'is_accident_free' in df.columns:
    accident = df[df['is_accident_free'] == 0]
    no_accident = df[df['is_accident_free'] == 1]
    print(f"  사고 이력 있음: {len(accident):,}건")
    print(f"  무사고: {len(no_accident):,}건")
    
    # 사고차 가격 차이
    if len(accident) > 100:
        common_models = df.groupby('Model').size().nlargest(10).index
        for model in common_models[:3]:
            acc_price = accident[accident['Model']==model]['Price'].median()
            no_acc_price = no_accident[no_accident['Model']==model]['Price'].median()
            if pd.notna(acc_price) and pd.notna(no_acc_price) and no_acc_price > 0:
                diff = (acc_price - no_acc_price) / no_acc_price * 100
                print(f"    {model}: 사고차 {acc_price:,.0f} vs 무사고 {no_acc_price:,.0f} ({diff:+.1f}%)")

# ============================================================
print("\n" + "="*80)
print("💡 권장 추가 이상치 처리")
print("="*80)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│  추가 권장 이상치 처리                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ 이미 구현됨:                                                    │
│     1. 중복 제거                                                    │
│     2. 패턴 가격 (1111, 9999 등)                                    │
│     3. 연간 주행거리 이상 (>4만km or <2천km)                        │
│     4. 모델+연식별 3σ 이상치                                        │
│                                                                     │
│  🔶 추가 권장:                                                      │
│     5. IQR 1.5배 방식 (3σ 대신 또는 병행)                           │
│     6. 주행거리-가격 역상관 이상치 (고주행+고가)                    │
│     7. 신차 대비 과도 감가 (1~2년차 + 평균 50% 미만)                │
│     8. Log 변환 후 Z-score > 3 제거                                 │
│     9. 극단 가격 (< 50만원 또는 > 신차가)                           │
│                                                                     │
│  ⚠️ 데이터 없어서 불가:                                             │
│     - 렌터카/리스 이력 분리                                         │
│     - 성능점검기록부 기반 사고 분류                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
""")
