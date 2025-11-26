"""
엔카 국산차 + 수입차 통합 전처리 스크립트
- 국산차 데이터: processed_encar_data.csv (기존)
- 수입차 데이터: encar_imported_data.csv (새로 수집)
- 통합 데이터: processed_encar_combined.csv
"""
import pandas as pd
import numpy as np
import os

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
    imported_file = "encar_imported_data.csv"
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
    
    # 이상치 제거 (차량 유형별로 다르게)
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
    
    print(f"   ✓ 이상치 제거 후: {len(df_combined):,}건")
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
