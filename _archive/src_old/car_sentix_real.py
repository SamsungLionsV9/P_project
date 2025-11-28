"""
Car-Sentix 타이밍 어드바이저 (실제 데이터 버전)
100% 객관적 데이터만 사용:
- 거시경제 지표 (금리, 환율, 유가)
- 검색 트렌드
- 신차 출시 일정
"""

import sys
import json
from datetime import datetime
from data_collectors_real_only import collect_real_data_only, save_collected_data
from timing_engine_real import RealTimingEngine


def analyze_timing_real(car_model):
    """
    실제 데이터 기반 타이밍 분석
    
    Args:
        car_model: 차량 모델명
        
    Returns:
        dict: 타이밍 분석 결과
    """
    print("=" * 80)
    print(f"🎯 Car-Sentix 타이밍 분석 (실제 데이터)")
    print("=" * 80)
    print()
    
    # [1/2] 데이터 수집
    print("[1/2] 실제 데이터 수집 중...")
    print("─" * 80)
    print()
    
    data = collect_real_data_only(car_model)
    
    print()
    
    # [2/2] 타이밍 점수 계산
    print("[2/2] 타이밍 점수 계산 중...")
    print("─" * 80)
    print()
    
    engine = RealTimingEngine()
    result = engine.calculate_timing_score(
        macro_data=data['macro'],
        trend_data=data['trend'],
        schedule_data=data['schedule'],
        car_model=car_model
    )
    
    # 결과 출력
    engine.print_result(result)
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # 1. 타이밍 점수 저장
    score_file = f"timing_score_real_{car_model}_{timestamp}.json"
    with open(score_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 2. 수집 데이터 저장
    data_file = save_collected_data(data, car_model)
    
    print()
    print("💾 결과 저장:")
    print(f"  - {score_file}")
    print(f"  - {data_file}")
    print()
    
    return result


def compare_multiple_cars_real(car_models):
    """
    여러 차량 비교 (실제 데이터)
    
    Args:
        car_models: 차량 모델명 리스트
        
    Returns:
        list: 타이밍 분석 결과 리스트
    """
    print("=" * 80)
    print(f"🎯 다중 차량 비교 분석 (실제 데이터)")
    print(f"대상 차량: {', '.join(car_models)}")
    print("=" * 80)
    print()
    
    results = []
    
    for i, car_model in enumerate(car_models, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(car_models)}] {car_model} 분석 중...")
        print(f"{'='*80}\n")
        
        result = analyze_timing_real(car_model)
        results.append(result)
        
        if i < len(car_models):
            print("\n" + "="*80)
            print("다음 차량 분석 준비 중...")
            print("="*80 + "\n")
    
    # 비교 요약
    print("\n" + "=" * 80)
    print("📊 종합 비교 결과")
    print("=" * 80)
    print()
    
    # 점수순 정렬
    sorted_results = sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    print(f"{'순위':<6} {'차량':<12} {'점수':<10} {'판단':<10} {'신뢰도':<8}")
    print("-" * 80)
    
    for rank, result in enumerate(sorted_results, 1):
        print(f"{rank:<6} {result['car_model']:<12} "
              f"{result['final_score']:.1f}점{'':<5} "
              f"{result['color']} {result['decision']:<8} "
              f"{result['confidence']:<8}")
    
    print()
    print("=" * 80)
    print()
    
    # 추천
    best = sorted_results[0]
    print(f"💡 추천: {best['car_model']} (점수: {best['final_score']:.1f}점)")
    print(f"   사유: {best['action']}")
    print()
    
    return results


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 80)
    print("🚗 Car-Sentix 타이밍 어드바이저 (실제 데이터 버전)")
    print("=" * 80)
    print()
    print("📊 데이터 출처:")
    print("  ✅ 거시경제: 한국은행 API + Yahoo Finance")
    print("  ✅ 검색 트렌드: 네이버 데이터랩 API")
    print("  ✅ 신차 일정: CSV 데이터")
    print("  ❌ 커뮤니티 감성: 제외 (100% 객관적 데이터만 사용)")
    print()
    print("=" * 80)
    print()
    
    # 명령줄 인자 확인
    if len(sys.argv) > 1:
        car_models = sys.argv[1:]
        
        if len(car_models) == 1:
            # 단일 차량 분석
            analyze_timing_real(car_models[0])
        else:
            # 다중 차량 비교
            compare_multiple_cars_real(car_models)
    else:
        # 대화형 입력
        print("🚗 차량 모델명을 입력하세요 (여러 개는 쉼표로 구분):")
        print("   예: 그랜저  또는  그랜저, 아반떼, K5")
        print()
        
        user_input = input(">>> ").strip()
        
        if not user_input:
            print("⚠️ 입력이 없습니다. 기본값 '그랜저'로 분석합니다.")
            car_models = ["그랜저"]
        else:
            car_models = [c.strip() for c in user_input.split(',')]
        
        print()
        
        if len(car_models) == 1:
            analyze_timing_real(car_models[0])
        else:
            compare_multiple_cars_real(car_models)
    
    print()
    print("=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
