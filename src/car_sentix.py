"""
Car-Sentix: 중고차 구매 타이밍 어드바이저
- 실시간 데이터 수집
- 타이밍 점수 계산
- 의사결정 지원
"""

import sys
from datetime import datetime
import json

from data_collectors_complete import collect_complete_data
from timing_engine import TimingScoreEngine


def analyze_car_timing(car_model, save_result=True):
    """
    특정 차량의 구매 타이밍 분석
    
    Args:
        car_model: 차량 모델명 (예: "그랜저", "아반떼", "K5")
        save_result: 결과 저장 여부
        
    Returns:
        dict: 타이밍 분석 결과
    """
    print("\n" + "=" * 80)
    print(f"🚗 Car-Sentix: '{car_model}' 구매 타이밍 분석")
    print("=" * 80)
    
    # 1단계: 데이터 수집
    print("\n[1/2] 실시간 데이터 수집 중...")
    print("─" * 80)
    
    try:
        collected_data = collect_complete_data(car_model)
    except Exception as e:
        print(f"\n❌ 데이터 수집 실패: {e}")
        return None
    
    # 2단계: 타이밍 점수 계산
    print("\n[2/2] 타이밍 점수 계산 중...")
    print("─" * 80)
    
    try:
        engine = TimingScoreEngine()
        result = engine.calculate_final_score(collected_data)
        engine.print_result(result)
    except Exception as e:
        print(f"\n❌ 점수 계산 실패: {e}")
        return None
    
    # 결과 저장
    if save_result:
        # 타이밍 점수
        score_file = f"timing_score_{car_model}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(score_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 수집 데이터 (요약만)
        data_file = f"collected_data_{car_model}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        save_data = collected_data.copy()
        if 'community' in save_data and 'posts' in save_data['community']:
            save_data['community']['posts_sample'] = [
                {
                    'title': p.get('title', ''),
                    'source': p.get('source', '')
                }
                for p in save_data['community']['posts'][:10]
            ]
            del save_data['community']['posts']
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장:")
        print(f"  - {score_file}")
        print(f"  - {data_file}")
    
    return result


def compare_multiple_cars(car_models):
    """
    여러 차량의 타이밍 비교
    
    Args:
        car_models: 차량 모델명 리스트
        
    Returns:
        list: 각 차량의 분석 결과
    """
    print("\n" + "=" * 80)
    print(f"🚗 Car-Sentix: {len(car_models)}개 차량 비교 분석")
    print("=" * 80)
    
    results = []
    
    for i, model in enumerate(car_models, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(car_models)}] {model} 분석 중...")
        print(f"{'=' * 80}")
        
        result = analyze_car_timing(model, save_result=False)
        if result:
            results.append(result)
    
    # 비교 요약
    if results:
        print("\n" + "=" * 80)
        print("📊 비교 요약")
        print("=" * 80)
        
        # 점수순 정렬
        sorted_results = sorted(results, key=lambda x: x['final_score'], reverse=True)
        
        print(f"\n{'순위':<4} {'차량':<15} {'점수':<8} {'판단':<15}")
        print("─" * 80)
        
        for i, r in enumerate(sorted_results, 1):
            print(f"{i:<4} {r['car_model']:<15} {r['final_score']:>5.1f}점  {r['decision']:<15}")
        
        print("─" * 80)
        
        # 최고/최저
        best = sorted_results[0]
        worst = sorted_results[-1]
        
        print(f"\n🏆 최고: {best['car_model']} ({best['final_score']:.1f}점, {best['decision']})")
        print(f"⚠️ 최저: {worst['car_model']} ({worst['final_score']:.1f}점, {worst['decision']})")
        
        # 비교 저장
        compare_file = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(compare_file, 'w', encoding='utf-8') as f:
            json.dump({
                'models': car_models,
                'results': results,
                'best': best['car_model'],
                'worst': worst['car_model'],
                'analyzed_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 비교 결과 저장: {compare_file}")
    
    return results


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚗 Car-Sentix: 중고차 구매 타이밍 어드바이저")
    print("=" * 80)
    print("\n실시간 데이터 기반 구매 의사결정 지원 시스템")
    print("- 거시경제 지표 (금리, 유가, 환율)")
    print("- 검색 트렌드 (네이버 데이터랩)")
    print("- 커뮤니티 감성 분석")
    print("- 신차 출시 일정")
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 차량 모델 전달
        car_models = sys.argv[1:]
        
        if len(car_models) == 1:
            # 단일 차량 분석
            analyze_car_timing(car_models[0])
        else:
            # 여러 차량 비교
            compare_multiple_cars(car_models)
    else:
        # 대화형 모드
        print("\n" + "─" * 80)
        print("사용 방법:")
        print("  1. 단일 차량 분석: python car_sentix.py 그랜저")
        print("  2. 여러 차량 비교: python car_sentix.py 그랜저 아반떼 K5")
        print("─" * 80)
        
        car_model = input("\n분석할 차량 모델을 입력하세요 (예: 그랜저): ").strip()
        
        if not car_model:
            print("❌ 차량 모델을 입력해주세요.")
            return
        
        analyze_car_timing(car_model)
    
    print("\n" + "=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
