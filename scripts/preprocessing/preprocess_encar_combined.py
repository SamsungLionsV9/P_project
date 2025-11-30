"""
엔카 국산차 + 수입차 통합 전처리 스크립트
- 국산차 데이터: processed_encar_data.csv (기존)
- 수입차 데이터: encar_imported_data.csv (새로 수집)
- 통합 데이터: processed_encar_combined.csv

v2.0 - 가격 이상치 필터링 강화 (연식 대비 비정상 가격 제거)
"""
import pandas as pd
import numpy as np
import os

# ========== 가격 필터 상수 ==========
# 엔카에서 "가격 미정", "가격 문의" 차량은 1, 11, 86 등 비정상적으로 낮은 가격으로 표시됨
# 이를 필터링하기 위한 연식 대비 최소 가격 기준

# 국산차 연식별 최소 가격 (만원) - 가격 미정 차량 필터링용
DOMESTIC_MIN_PRICE_BY_AGE = {
    0: 500,    # 신차급 (2024-2025)
    1: 400,    # 1년
    2: 300,    # 2년
    3: 250,    # 3년
    4: 200,    # 4년
    5: 150,    # 5년
    10: 100,   # 10년
    15: 50,    # 15년
    20: 30,    # 20년 이상
}

# 외제차 연식별 최소 가격 (만원) - 일반적으로 국산차보다 높음
IMPORTED_MIN_PRICE_BY_AGE = {
    0: 1000,   # 신차급 (2024-2025)
    1: 800,    # 1년
    2: 600,    # 2년
    3: 500,    # 3년
    4: 400,    # 4년
    5: 300,    # 5년
    10: 200,   # 10년
    15: 100,   # 15년
    20: 50,    # 20년 이상
}

def get_min_price_by_age(age: int, is_imported: bool) -> int:
    """연식에 따른 최소 가격 반환"""
    price_table = IMPORTED_MIN_PRICE_BY_AGE if is_imported else DOMESTIC_MIN_PRICE_BY_AGE

    # 정확히 일치하는 연식이 있으면 반환
    if age in price_table:
        return price_table[age]

    # 없으면 가장 가까운 값 찾기
    ages = sorted(price_table.keys())
    for i, a in enumerate(ages):
        if age < a:
            if i == 0:
                return price_table[ages[0]]
            # 이전 연식과 현재 연식 사이에서 보간
            prev_age = ages[i-1]
            prev_price = price_table[prev_age]
            curr_price = price_table[a]
            ratio = (age - prev_age) / (a - prev_age)
            return int(prev_price + (curr_price - prev_price) * ratio)

    # 가장 오래된 연식보다 더 오래됨
    return price_table[ages[-1]]


def preprocess_combined_data():
    print("🔧 엔카 데이터 통합 전처리 시작...")
    print("=" * 70)
    
    # ---------------------------------------------------------
    # 1. 국산차 데이터 로드
    # ---------------------------------------------------------
    domestic_file = "data/processed_encar_data.csv"
    if not os.path.exists(domestic_file):
        print(f"❌ 국산차 데이터 파일을 찾을 수 없습니다: {domestic_file}")
        return
    
    print(f"\n📂 국산차 데이터 로딩: {domestic_file}")
    df_domestic = pd.read_csv(domestic_file)
    
    # 컬럼명 소문자 통일
    df_domestic.columns = df_domestic.columns.str.lower()
    
    # CarType 컬럼이 없으면 추가
    if 'car_type' not in df_domestic.columns:
        df_domestic['car_type'] = 'Domestic'
    
    print(f"   ✓ 국산차: {len(df_domestic):,}건")
    print(f"   컬럼: {list(df_domestic.columns)}")
    
    # ---------------------------------------------------------
    # 2. 수입차 데이터 로드
    # ---------------------------------------------------------
    imported_file = "data/encar_imported_data.csv"
    if not os.path.exists(imported_file):
        print(f"\n⚠️  수입차 데이터 파일을 찾을 수 없습니다: {imported_file}")
        print("   수입차 없이 국산차만 사용합니다.")
        df_imported = pd.DataFrame()
    else:
        print(f"\n📂 수입차 데이터 로딩: {imported_file}")
        df_imported = pd.read_csv(imported_file)
        
        # 컬럼명 소문자 통일
        df_imported.columns = df_imported.columns.str.lower()
        
        print(f"   ✓ 수입차: {len(df_imported):,}건")
        print(f"   컬럼: {list(df_imported.columns)}")
    
    # ---------------------------------------------------------
    # 3. 데이터 병합 (컬럼명 통일 후)
    # ---------------------------------------------------------
    if len(df_imported) > 0:
        print(f"\n🔗 데이터 병합 중...")
        
        # 수입차 데이터 컬럼명 매핑
        imported_mapping = {
            'manufacturer': 'brand',
            'model': 'model_name',
            'fueltype': 'fuel',
            'cartype': 'car_type'
        }
        df_imported = df_imported.rename(columns=imported_mapping)
        
        # 필요한 컬럼 선택
        required_cols = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price', 'car_type']
        
        # 국산차 데이터에서 필요 컬럼만 선택
        domestic_cols = [col for col in required_cols if col in df_domestic.columns]
        df_domestic_selected = df_domestic[domestic_cols].copy()
        
        # 수입차 데이터에서 필요 컬럼만 선택
        imported_cols = [col for col in required_cols if col in df_imported.columns]
        df_imported_selected = df_imported[imported_cols].copy()
        
        print(f"   국산차 컬럼: {domestic_cols}")
        print(f"   수입차 컬럼: {imported_cols}")
        
        # 병합
        df_combined = pd.concat([
            df_domestic_selected,
            df_imported_selected
        ], ignore_index=True)
        
        print(f"   ✓ 통합 데이터: {len(df_combined):,}건")
    else:
        df_combined = df_domestic.copy()
        print(f"\n⚠️  수입차 데이터 없음 - 국산차만 사용")
    
    # ---------------------------------------------------------
    # 4. 데이터 전처리
    # ---------------------------------------------------------
    print(f"\n🔧 데이터 전처리 중...")
    print(f"   현재 컬럼: {list(df_combined.columns)}")
    
    # 필수 컬럼 확인
    required_cols = ['brand', 'model_name', 'year', 'mileage', 'fuel', 'price']
    missing_cols = [col for col in required_cols if col not in df_combined.columns]
    if missing_cols:
        print(f"   ⚠️  누락된 컬럼: {missing_cols}")
        # 누락된 컬럼은 'Unknown'으로 채움
        for col in missing_cols:
            df_combined[col] = 'Unknown'
    
    # 결측치 제거
    initial_count = len(df_combined)
    df_combined = df_combined.dropna(subset=['year', 'mileage', 'price'])
    print(f"   ✓ 결측치 제거: {initial_count:,} → {len(df_combined):,}건 ({initial_count - len(df_combined):,}건 제거)")
    
    # 데이터 타입 변환
    df_combined['year'] = pd.to_numeric(df_combined['year'], errors='coerce')
    df_combined['mileage'] = pd.to_numeric(df_combined['mileage'], errors='coerce')
    df_combined['price'] = pd.to_numeric(df_combined['price'], errors='coerce')
    
    # Year 컬럼이 YYYYMM 형식인 경우 연도만 추출
    df_combined['year'] = df_combined['year'].apply(lambda x: int(x // 100) if x > 2025 else x)
    
    # ---------------------------------------------------------
    # 4-1. 기본 이상치 제거 (차량 유형별로 다르게)
    # ---------------------------------------------------------
    print(f"   이상치 제거 전: 국산차 {len(df_combined[df_combined['car_type']=='Domestic']):,}건, 수입차 {len(df_combined[df_combined['car_type']=='Imported']):,}건")

    # 공통 조건
    common_filter = (
        (df_combined['year'] >= 1990) &
        (df_combined['year'] <= 2025) &
        (df_combined['mileage'] >= 0) &
        (df_combined['mileage'] <= 500000) &
        (df_combined['price'] > 0)
    )

    # 국산차: 5억원 이하
    domestic_filter = common_filter & (df_combined['car_type'] == 'Domestic') & (df_combined['price'] <= 50000)

    # 수입차: 10억원 이하 (고가 차량 보존)
    imported_filter = common_filter & (df_combined['car_type'] == 'Imported') & (df_combined['price'] <= 100000)

    # 두 조건 합치기
    df_combined = df_combined[domestic_filter | imported_filter]

    print(f"   ✓ 기본 이상치 제거 후: {len(df_combined):,}건")
    print(f"      - 국산차: {len(df_combined[df_combined['car_type']=='Domestic']):,}건")
    print(f"      - 수입차: {len(df_combined[df_combined['car_type']=='Imported']):,}건")

    # ---------------------------------------------------------
    # 4-2. 연식 대비 비정상 가격 필터링 (가격 미정/문의 차량 제거)
    # ---------------------------------------------------------
    print(f"\n   🔍 연식 대비 비정상 가격 필터링...")

    # 연식 계산 (2025년 기준)
    df_combined['age'] = 2025 - df_combined['year']

    # 연식별 최소 가격 계산
    def check_price_validity(row):
        """연식 대비 가격이 정상인지 확인"""
        age = int(row['age']) if pd.notna(row['age']) else 0
        price = row['price']
        is_imported = row['car_type'] == 'Imported'

        min_price = get_min_price_by_age(age, is_imported)
        return price >= min_price

    before_filter = len(df_combined)

    # 비정상 가격 차량 로깅
    invalid_mask = ~df_combined.apply(check_price_validity, axis=1)
    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        print(f"   ⚠️  연식 대비 비정상 가격 차량 {invalid_count}건 발견:")
        invalid_samples = df_combined[invalid_mask][['brand', 'model_name', 'year', 'price', 'car_type']].head(10)
        for _, row in invalid_samples.iterrows():
            age = 2025 - int(row['year'])
            min_price = get_min_price_by_age(age, row['car_type'] == 'Imported')
            print(f"      - {row['brand']} {row['model_name']} ({int(row['year'])}년): {row['price']:.0f}만원 (최소 {min_price}만원 필요)")

    # 정상 가격 차량만 유지
    df_combined = df_combined[~invalid_mask]

    # age 컬럼 제거 (임시 컬럼)
    df_combined = df_combined.drop(columns=['age'])

    print(f"   ✓ 연식 대비 비정상 가격 필터링 후: {len(df_combined):,}건 ({before_filter - len(df_combined):,}건 제거)")
    print(f"      - 국산차: {len(df_combined[df_combined['car_type']=='Domestic']):,}건")
    print(f"      - 수입차: {len(df_combined[df_combined['car_type']=='Imported']):,}건")
    
    # 중복 제거
    if 'id' in df_combined.columns:
        df_combined = df_combined.drop_duplicates(subset=['id'])
        print(f"   ✓ 중복 제거 후: {len(df_combined):,}건")
    
    # ---------------------------------------------------------
    # 5. 최종 저장
    # ---------------------------------------------------------
    output_file = "data/processed_encar_combined.csv"
    df_combined.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print(f"✅ 통합 데이터 전처리 완료!")
    print(f"📁 저장 위치: {os.path.abspath(output_file)}")
    print(f"📊 최종 데이터: {len(df_combined):,}건")
    
    # ---------------------------------------------------------
    # 6. 통계 요약
    # ---------------------------------------------------------
    print("\n📊 데이터 통계 요약")
    print("-" * 70)
    
    if 'car_type' in df_combined.columns:
        print("\n🚗 차량 유형별 분포:")
        print(df_combined['car_type'].value_counts())
    
    if 'brand' in df_combined.columns:
        print("\n🏭 브랜드별 Top 10:")
        print(df_combined['brand'].value_counts().head(10))
    
    print(f"\n📈 가격 통계:")
    print(f"   평균: {df_combined['price'].mean():.0f}만원")
    print(f"   중위수: {df_combined['price'].median():.0f}만원")
    print(f"   최소: {df_combined['price'].min():.0f}만원")
    print(f"   최대: {df_combined['price'].max():.0f}만원")
    
    print(f"\n🏃 주행거리 통계:")
    print(f"   평균: {df_combined['mileage'].mean():,.0f}km")
    print(f"   중위수: {df_combined['mileage'].median():,.0f}km")
    
    print(f"\n📅 연식 통계:")
    print(f"   최신: {df_combined['year'].max():.0f}년")
    print(f"   최구: {df_combined['year'].min():.0f}년")
    print(f"   평균: {df_combined['year'].mean():.0f}년")
    
    return df_combined

if __name__ == "__main__":
    preprocess_combined_data()
