import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.font_manager as fm

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def create_visualizations(data_path='../data/processed_encar_data.csv', save_dir='../docs/images'):
    """데이터 분석 보고서용 그래프 생성"""
    
    print("📊 데이터 시각화 생성 시작...")
    
    # 1. 데이터 로드
    if not os.path.exists(data_path):
        print(f"❌ 데이터 파일을 찾을 수 없습니다: {data_path}")
        # 테스트용 더미 데이터 생성 (실제 파일이 없을 경우)
        print("⚠️ 테스트용 더미 데이터를 생성합니다.")
        data = pd.DataFrame({
            'Price': np.random.lognormal(3, 1, 1000) * 100,
            'Year': np.random.randint(2015, 2024, 1000),
            'Mileage': np.random.randint(1000, 150000, 1000),
            'Brand': np.random.choice(['Hyundai', 'Kia', 'BMW', 'Benz'], 1000)
        })
        # 가격과 연관성 추가
        data['Price'] = data['Year'] * 100 - data['Mileage'] * 0.05 + np.random.normal(0, 500, 1000)
        data['Price'] = data['Price'].clip(lower=500)
    else:
        data = pd.read_csv(data_path)
        print(f"✓ 데이터 로드 완료: {len(data):,}건")
        
        # 컬럼명 통일 (소문자 -> 대문자 첫글자)
        data = data.rename(columns={
            'price': 'Price', 
            'year': 'Year', 
            'mileage': 'Mileage',
            'brand': 'Brand',
            'model_name': 'Model'
        })

    # 저장 디렉토리 생성
    os.makedirs(save_dir, exist_ok=True)

    # 스타일 설정
    sns.set_theme(style="whitegrid", font='Malgun Gothic')

    # ---------------------------------------------------------
    # 1. 가격 분포 그래프 (원본 + 로그 변환 비교)
    # ---------------------------------------------------------
    print("📈 1. 가격 분포 그래프 생성 중...")
    
    # 이상치 제거 (99 percentile 이하만 사용)
    price_99 = data['Price'].quantile(0.99)
    filtered_data = data[data['Price'] <= price_99]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 1-1. 원본 가격 분포
    sns.histplot(filtered_data['Price'], kde=True, bins=60, 
                 color='#3498db', edgecolor='white', ax=axes[0])
    axes[0].set_title('원본 가격 분포 (Original)', fontsize=18, fontweight='bold', pad=20)
    axes[0].set_xlabel('가격 (만원)', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('빈도수', fontsize=14, fontweight='bold')
    axes[0].tick_params(labelsize=12)
    axes[0].grid(True, alpha=0.3)
    
    # 통계량 표시
    stats_text = f"평균: {data['Price'].mean():.0f}만원\n중위수: {data['Price'].median():.0f}만원\n표준편차: {data['Price'].std():.0f}만원"
    axes[0].text(0.95, 0.95, stats_text, transform=axes[0].transAxes, 
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                 fontsize=12, fontweight='bold')
    
    # 1-2. 로그 변환 가격 분포
    log_price = np.log1p(filtered_data['Price'])
    sns.histplot(log_price, kde=True, bins=60, 
                 color='#e74c3c', edgecolor='white', ax=axes[1])
    axes[1].set_title('로그 변환 후 분포 (Log Transformed)', fontsize=18, fontweight='bold', pad=20)
    axes[1].set_xlabel('log(가격 + 1)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('빈도수', fontsize=14, fontweight='bold')
    axes[1].tick_params(labelsize=12)
    axes[1].grid(True, alpha=0.3)
    
    # 정규분포 설명
    axes[1].text(0.05, 0.95, '정규분포에 가까워짐\n→ ML 학습에 적합', 
                 transform=axes[1].transAxes, 
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
                 fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'price_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 저장 완료: price_distribution.png")

    # ---------------------------------------------------------
    # 2. 연식별 가격 분포 (Violin + 평균선)
    # ---------------------------------------------------------
    print("📈 2. 연식별 가격 분포 생성 중...")
    
    # 최근 10년 데이터만 사용 (가독성)
    recent_years = data[data['Year'] >= 2015].copy()
    recent_years = recent_years[recent_years['Price'] <= recent_years['Price'].quantile(0.95)]
    
    plt.figure(figsize=(14, 7))
    
    # Violin Plot (분포 + 박스플롯)
    ax = sns.violinplot(x='Year', y='Price', data=recent_years, 
                        palette='coolwarm', inner='box', linewidth=1.5)
    
    # 평균값 라인 추가
    year_means = recent_years.groupby('Year')['Price'].mean()
    years = sorted(recent_years['Year'].unique())
    plt.plot(range(len(years)), year_means.values, 
             color='red', marker='o', linewidth=3, markersize=8, 
             label='평균 가격', zorder=10)
    
    plt.title('연식별 가격 분포 및 평균 추세 (2015-2023)', 
              fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('연식 (Year)', fontsize=16, fontweight='bold')
    plt.ylabel('가격 (만원)', fontsize=16, fontweight='bold')
    plt.xticks(rotation=0, fontsize=13, fontweight='bold')
    plt.yticks(fontsize=13)
    plt.legend(fontsize=14, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')
    
    # 추세 설명
    price_increase = year_means.iloc[-1] - year_means.iloc[0]
    plt.text(0.5, 0.98, f'최근 {len(years)}년간 평균 {price_increase:.0f}만원 상승', 
             transform=plt.gca().transAxes, 
             verticalalignment='top', horizontalalignment='center',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
             fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'price_by_year.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 저장 완료: price_by_year.png")

    # ---------------------------------------------------------
    # 3. 주행거리 감가상각 곡선 (밀도 히트맵 + 회귀선)
    # ---------------------------------------------------------
    print("📈 3. 주행거리 감가상각 곡선 생성 중...")
    
    # 이상치 제거
    mileage_data = data[(data['Mileage'] <= 200000) & 
                        (data['Price'] <= data['Price'].quantile(0.95))].copy()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Hexbin (밀도 기반 히트맵) - 데이터가 많을 때 효과적
    hexbin = ax.hexbin(mileage_data['Mileage'], mileage_data['Price'], 
                       gridsize=50, cmap='YlOrRd', alpha=0.8, mincnt=1)
    
    # 회귀선 (2차 곡선)
    from scipy.stats import linregress
    from numpy.polynomial import Polynomial
    
    # 2차 다항식 피팅
    p = Polynomial.fit(mileage_data['Mileage'], mileage_data['Price'], deg=2)
    x_line = np.linspace(mileage_data['Mileage'].min(), mileage_data['Mileage'].max(), 100)
    y_line = p(x_line)
    
    ax.plot(x_line, y_line, color='blue', linewidth=4, 
            label='감가상각 곡선 (2차 다항식)', zorder=10)
    
    # 컬러바
    cbar = plt.colorbar(hexbin, ax=ax)
    cbar.set_label('데이터 밀도', fontsize=14, fontweight='bold')
    
    plt.title('주행거리별 감가상각 곡선 (Mileage-based Depreciation)', 
              fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('주행거리 (km)', fontsize=16, fontweight='bold')
    plt.ylabel('가격 (만원)', fontsize=16, fontweight='bold')
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # 핵심 구간 강조
    ax.axvline(x=100000, color='red', linestyle='--', linewidth=2, alpha=0.7, 
               label='10만km (급격한 하락 구간)')
    plt.legend(fontsize=12, loc='upper right')
    
    # 설명 추가
    plt.text(0.05, 0.25, 
             '✓ 주행거리 증가 → 비선형 가격 하락\n✓ 10만km 이후 급격한 감가상각\n✓ 색이 진할수록 데이터 집중', 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9),
             fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'depreciation_curve.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 저장 완료: depreciation_curve.png")

    print(f"\n✅ 모든 그래프 생성 완료!")
    print(f"📁 저장 위치: {os.path.abspath(save_dir)}")
    print(f"   - price_distribution.png (가격 분포)")
    print(f"   - price_by_year.png (연식별 가격)")
    print(f"   - depreciation_curve.png (주행거리 감가상각)")

if __name__ == "__main__":
    create_visualizations()
