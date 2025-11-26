"""데이터 분석 시각화 생성 - 보고서/논문용"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = Path('docs/figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {'domestic': '#3B82F6', 'imported': '#8B5CF6', 'accent': '#10B981'}

print("="*60)
print("📊 데이터 시각화 생성")
print("="*60)

# 데이터 로드
try:
    domestic_df = pd.read_csv('encar_raw_domestic.csv')
    print(f"국산차: {len(domestic_df):,}건")
except: domestic_df = None

try:
    imported_df = pd.read_csv('encar_imported_data.csv')
    print(f"외제차: {len(imported_df):,}건")
except: imported_df = None

# ============ 그림 1: 가격 분포 ============
print("\n📈 그림 1: 가격 분포...")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

if domestic_df is not None:
    prices = domestic_df['Price'].dropna()
    prices = prices[(prices > 100) & (prices < 30000)]
    axes[0,0].hist(prices, bins=50, color=COLORS['domestic'], alpha=0.7, edgecolor='white')
    axes[0,0].set_title('국산차 가격 분포 (원본)', fontweight='bold')
    axes[0,0].axvline(prices.median(), color='red', linestyle='--', label=f'중앙값: {prices.median():,.0f}')
    axes[0,0].legend()
    axes[0,1].hist(np.log1p(prices), bins=50, color=COLORS['domestic'], alpha=0.7)
    axes[0,1].set_title('국산차 가격 (로그 변환)', fontweight='bold')

if imported_df is not None:
    prices = imported_df['Price'].dropna()
    prices = prices[(prices > 100) & (prices < 50000)]
    axes[1,0].hist(prices, bins=50, color=COLORS['imported'], alpha=0.7, edgecolor='white')
    axes[1,0].set_title('외제차 가격 분포 (원본)', fontweight='bold')
    axes[1,0].axvline(prices.median(), color='red', linestyle='--', label=f'중앙값: {prices.median():,.0f}')
    axes[1,0].legend()
    axes[1,1].hist(np.log1p(prices), bins=50, color=COLORS['imported'], alpha=0.7)
    axes[1,1].set_title('외제차 가격 (로그 변환)', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig1_price_distribution.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig1_price_distribution.png'}")

# ============ 그림 2: 브랜드 분포 ============
print("📈 그림 2: 브랜드 분포...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

if domestic_df is not None:
    bc = domestic_df['Manufacturer'].value_counts().head(8)
    axes[0].barh(bc.index[::-1], bc.values[::-1], color=plt.cm.Blues(np.linspace(0.4,0.8,8))[::-1])
    axes[0].set_title('국산차 제조사별 분포', fontweight='bold')
    for i, v in enumerate(bc.values[::-1]):
        axes[0].text(v+300, i, f'{v/bc.sum()*100:.1f}%', va='center')

if imported_df is not None:
    bc = imported_df['Manufacturer'].value_counts().head(8)
    axes[1].barh(bc.index[::-1], bc.values[::-1], color=plt.cm.Purples(np.linspace(0.4,0.8,8))[::-1])
    axes[1].set_title('외제차 제조사별 분포', fontweight='bold')
    for i, v in enumerate(bc.values[::-1]):
        axes[1].text(v+100, i, f'{v/bc.sum()*100:.1f}%', va='center')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig2_brand_distribution.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig2_brand_distribution.png'}")

# ============ 그림 3: 알고리즘 비교 ============
print("📈 그림 3: 알고리즘 비교...")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
algs = ['Linear\nRegression', 'Random\nForest', 'LightGBM', 'XGBoost']
mape = [22.3, 14.2, 10.5, 9.9]
r2 = [0.82, 0.91, 0.95, 0.97]
colors = ['#94A3B8']*3 + ['#10B981']

axes[0].bar(algs, mape, color=colors)
axes[0].set_title('알고리즘별 MAPE 비교', fontweight='bold')
axes[0].axhline(10, color='red', linestyle='--', alpha=0.5)
for i, v in enumerate(mape): axes[0].text(i, v+0.5, f'{v}%', ha='center', fontweight='bold')

axes[1].bar(algs, r2, color=colors)
axes[1].set_title('알고리즘별 R² 비교', fontweight='bold')
axes[1].set_ylim(0.75, 1.0)
for i, v in enumerate(r2): axes[1].text(i, v+0.005, f'{v:.2f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig3_algorithm_comparison.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig3_algorithm_comparison.png'}")

# ============ 그림 4: 피처 중요도 ============
print("📈 그림 4: 피처 중요도...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
d_feat = {'Model_Year_MG_enc':45.2,'Model_Year_enc':22.1,'Model_enc':12.3,'Mileage':8.5,'Age':5.2,'Opt_Premium':3.1,'Brand_Tier':2.1,'is_accident_free':1.5}
i_feat = {'Model_Year_MG_enc':38.5,'Model_Year_enc':18.2,'Class_Year_enc':12.1,'Brand_Tier':9.7,'Model_enc':8.3,'Mileage':6.2,'Class_enc':4.1,'Age':2.9}

axes[0].barh(list(d_feat.keys())[::-1], list(d_feat.values())[::-1], color=plt.cm.Blues(np.linspace(0.3,0.8,8))[::-1])
axes[0].set_title('국산차 (V11) 피처 중요도', fontweight='bold')
axes[1].barh(list(i_feat.keys())[::-1], list(i_feat.values())[::-1], color=plt.cm.Purples(np.linspace(0.3,0.8,8))[::-1])
axes[1].set_title('외제차 (V13) 피처 중요도', fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig4_feature_importance.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig4_feature_importance.png'}")

# ============ 그림 5: 서열 검증 ============
print("📈 그림 5: 서열 검증...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].bar(['C-클래스','E-클래스','S-클래스'], [5192,6496,13135], color=['#60A5FA','#3B82F6','#1D4ED8'])
axes[0].set_title('벤츠 클래스별 가격', fontweight='bold')
axes[1].bar(['3시리즈','5시리즈','7시리즈'], [3646,4529,9345], color=['#A78BFA','#8B5CF6','#6D28D9'])
axes[1].set_title('BMW 시리즈별 가격', fontweight='bold')
axes[2].bar(['A4','A6','A8'], [3437,4689,4880], color=['#34D399','#10B981','#059669'])
axes[2].set_title('아우디 모델별 가격', fontweight='bold')
for ax in axes: ax.set_ylabel('예측가격 (만원)')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig5_hierarchy_validation.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig5_hierarchy_validation.png'}")

# ============ 그림 6: 옵션 프리미엄 ============
print("📈 그림 6: 옵션 프리미엄...")
fig, ax = plt.subplots(figsize=(10, 6))
opts = ['통풍시트','썬루프','LED램프','가죽시트','네비게이션','열선시트','스마트키','후방카메라']
d_prem = [37,44,80,43,42,35,42,33]
i_prem = [120,100,100,80,80,60,50,50]
x = np.arange(len(opts))
ax.bar(x-0.2, d_prem, 0.4, label='국산차', color=COLORS['domestic'])
ax.bar(x+0.2, i_prem, 0.4, label='외제차', color=COLORS['imported'])
ax.set_xticks(x); ax.set_xticklabels(opts, rotation=45, ha='right')
ax.set_ylabel('프리미엄 (만원)'); ax.legend()
ax.set_title('옵션별 가격 프리미엄', fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig6_option_premium.png', dpi=150)
plt.close()
print(f"   ✓ {OUTPUT_DIR / 'fig6_option_premium.png'}")

print("\n" + "="*60)
print(f"✅ 총 6개 시각화 생성 완료: {OUTPUT_DIR}")
print("="*60)
