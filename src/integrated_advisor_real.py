"""
통합 어드바이저 (실제 데이터 버전)
Track 1: 가격 예측
Track 2: 타이밍 분석 (실제 데이터만)
"""

import sys
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import json

from data_collectors_real_only import collect_real_data_only
from timing_engine_real import RealTimingEngine


def load_price_model():
    """가격 예측 모델 로드"""
    # 모델 경로 찾기
    possible_paths = [
        '../models/improved_car_price_model.pkl',
        '../models/car_price_model.pkl',
        '../models/xgboost_model.pkl',
        'models/improved_car_price_model.pkl',
        'models/car_price_model.pkl',
        'car_price_model.pkl'
    ]
    
    for model_path in possible_paths:
        if os.path.exists(model_path):
            print(f"  ✓ 모델 로드: {model_path}")
            with open(model_path, 'rb') as f:
                return pickle.load(f)
    
    raise FileNotFoundError("❌ 가격 예측 모델을 찾을 수 없습니다")


def predict_price(brand, model, year, mileage, fuel):
    """
    차량 가격 예측
    
    Args:
        brand: 제조사
        model: 모델명
        year: 연식
        mileage: 주행거리
        fuel: 연료
        
    Returns:
        float: 예측 가격 (만원)
    """
    print("💰 가격 예측 중...")
    
    try:
        # 모델 로드
        price_model = load_price_model()
        
        # 입력 데이터 생성
        input_data = pd.DataFrame({
            'brand': [brand],
            'model': [model],
            'year': [year],
            'mileage': [mileage],
            'fuel': [fuel]
        })
        
        # Feature Engineering (predict_car_price.py와 동일)
        input_data['age'] = 2025 - input_data['year']
        input_data['mileage_per_year'] = input_data['mileage'] / (input_data['age'] + 1)
        input_data['is_low_mileage'] = (input_data['mileage'] < 30000).astype(int)
        input_data['is_high_mileage'] = (input_data['mileage'] > 150000).astype(int)
        
        # age_group
        input_data['age_group'] = pd.cut(
            input_data['age'],
            bins=[-1, 1, 3, 5, 10, 100],
            labels=['new', 'semi_new', 'used', 'old', 'very_old']
        )
        
        # brand_fuel
        input_data['brand_fuel'] = input_data['brand'] + '_' + input_data['fuel']
        
        # model_popularity_log (기본값)
        input_data['model_popularity_log'] = 5.0
        
        # premium brands
        premium_brands = ['벤츠', '비엠더블유', '아우디', '렉서스', '제네시스', '포르쉐', '볼보', '재규어', '랜드로버']
        input_data['is_premium'] = input_data['brand'].isin(premium_brands).astype(int)
        input_data['premium_age'] = input_data['is_premium'] * input_data['age']
        input_data['premium_mileage'] = input_data['is_premium'] * input_data['mileage']
        
        # mileage_vs_brand_avg (기본값)
        input_data['mileage_vs_brand_avg'] = 1.0
        
        # is_eco
        input_data['is_eco'] = input_data['fuel'].str.contains('전기|하이브리드', na=False).astype(int)
        
        # 예측
        predicted_price = price_model.predict(input_data)[0]
        
        print(f"  ✓ 예측 가격: {predicted_price:,.0f}만원")
        
        return predicted_price
        
    except Exception as e:
        print(f"  ⚠️ 가격 예측 실패: {e}")
        return None


def integrated_analysis_real(brand, model, year, mileage, fuel):
    """
    통합 분석 (실제 데이터)
    
    Args:
        brand: 제조사
        model: 모델명
        year: 연식
        mileage: 주행거리
        fuel: 연료
        
    Returns:
        dict: 통합 분석 결과
    """
    print("=" * 80)
    print("🎯 통합 어드바이저 (실제 데이터 버전)")
    print("=" * 80)
    print()
    print(f"🚗 차량 정보:")
    print(f"  제조사: {brand}")
    print(f"  모델: {model}")
    print(f"  연식: {year}년")
    print(f"  주행거리: {mileage:,}km")
    print(f"  연료: {fuel}")
    print()
    print("=" * 80)
    print()
    
    # Track 1: 가격 예측
    print("📍 Track 1: 가격 예측")
    print("─" * 80)
    predicted_price = predict_price(brand, model, year, mileage, fuel)
    print()
    
    # Track 2: 타이밍 분석 (실제 데이터)
    print("📍 Track 2: 타이밍 분석 (실제 데이터)")
    print("─" * 80)
    print()
    
    # 데이터 수집
    data = collect_real_data_only(model)
    
    print()
    
    # 타이밍 점수 계산
    engine = RealTimingEngine()
    timing_result = engine.calculate_timing_score(
        macro_data=data['macro'],
        trend_data=data['trend'],
        schedule_data=data['schedule'],
        car_model=model
    )
    
    # 통합 결과
    result = {
        'vehicle': {
            'brand': brand,
            'model': model,
            'year': year,
            'mileage': mileage,
            'fuel': fuel
        },
        'price_prediction': {
            'predicted_price': predicted_price,
            'unit': '만원'
        },
        'timing_analysis': timing_result,
        'data_sources': {
            'price': '학습된 XGBoost 모델 (119,343대)',
            'macro': '한국은행 API + Yahoo Finance',
            'trend': '네이버 데이터랩 API',
            'schedule': 'CSV 데이터'
        },
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 결과 출력
    print()
    print("=" * 80)
    print("📊 통합 분석 결과")
    print("=" * 80)
    print()
    
    # 가격
    if predicted_price:
        print(f"💰 예상 가격: {predicted_price:,.0f}만원")
        print()
    
    # 타이밍 출력
    engine.print_result(timing_result)
    
    # 종합 조언
    print()
    print("=" * 80)
    print("💡 종합 조언")
    print("=" * 80)
    print()
    
    if predicted_price and timing_result['final_score'] >= 70:
        print("✅ 구매 적기!")
        print(f"   예상 가격: {predicted_price:,.0f}만원")
        print(f"   타이밍 점수: {timing_result['final_score']:.1f}점")
        print("   → 적극 구매 추천")
    elif predicted_price and timing_result['final_score'] >= 55:
        print("⚠️ 관망 추천")
        print(f"   예상 가격: {predicted_price:,.0f}만원")
        print(f"   타이밍 점수: {timing_result['final_score']:.1f}점")
        print("   → 1-2주 후 재검토 권장")
    else:
        print("🔴 대기 권장")
        if predicted_price:
            print(f"   예상 가격: {predicted_price:,.0f}만원")
        print(f"   타이밍 점수: {timing_result['final_score']:.1f}점")
        print("   → 구매 시기 재고려 추천")
    
    print()
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"integrated_analysis_real_{model}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        # timing_result 내의 numpy 타입 변환
        result_copy = result.copy()
        if 'timing_analysis' in result_copy and 'scores' in result_copy['timing_analysis']:
            scores = result_copy['timing_analysis']['scores']
            for key in scores:
                if isinstance(scores[key], (np.integer, np.floating)):
                    scores[key] = float(scores[key])
        
        json.dump(result_copy, f, ensure_ascii=False, indent=2)
    
    print(f"💾 결과 저장: {filename}")
    print()
    print("=" * 80)
    
    return result


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 80)
    print("🚗 통합 어드바이저 (실제 데이터 버전)")
    print("=" * 80)
    print()
    print("📊 분석 내용:")
    print("  Track 1: 가격 예측 (XGBoost 모델)")
    print("  Track 2: 타이밍 분석 (실제 데이터)")
    print()
    print("📊 데이터 출처:")
    print("  ✅ 가격: 학습된 모델 (119,343대)")
    print("  ✅ 거시경제: 한국은행 API + Yahoo Finance")
    print("  ✅ 검색 트렌드: 네이버 데이터랩 API")
    print("  ✅ 신차 일정: CSV 데이터")
    print()
    print("=" * 80)
    print()
    
    # 명령줄 인자 확인
    if len(sys.argv) >= 6:
        brand = sys.argv[1]
        model = sys.argv[2]
        year = int(sys.argv[3])
        mileage = int(sys.argv[4])
        fuel = sys.argv[5]
    else:
        # 대화형 입력
        print("🚗 차량 정보를 입력하세요:")
        print()
        
        brand = input("제조사 (예: 현대, 기아, 벤츠): ").strip() or "현대"
        model = input("모델명 (예: 그랜저, 아반떼): ").strip() or "그랜저"
        year = int(input("연식 (예: 2022): ").strip() or "2022")
        mileage = int(input("주행거리 (예: 50000): ").strip() or "50000")
        fuel = input("연료 (가솔린/디젤/LPG/하이브리드/전기): ").strip() or "가솔린"
        
        print()
    
    # 통합 분석 실행
    integrated_analysis_real(brand, model, year, mileage, fuel)
    
    print()
    print("=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
