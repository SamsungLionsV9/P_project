"""
스마트 중고차 어드바이저 (Groq LLM 통합)
데이터 분석 + AI 자문 = 최강 조합
"""

import sys
from datetime import datetime
import json
from groq_advisor import GroqCarAdvisor
from integrated_advisor_real import predict_price
from data_collectors_real_only import collect_real_data_only
from timing_engine_real import RealTimingEngine


def smart_analysis(brand, model, year, mileage, fuel, sale_price, 
                   dealer_description="", performance_record=None,
                   use_groq=True):
    """
    스마트 분석: 데이터 분석 + Groq AI 자문
    
    Args:
        brand: 제조사
        model: 모델명
        year: 연식
        mileage: 주행거리
        fuel: 연료
        sale_price: 판매가 (만원)
        dealer_description: 딜러 설명글
        performance_record: 성능기록부
        use_groq: Groq 사용 여부
        
    Returns:
        dict: 종합 분석 결과
    """
    print("=" * 80)
    print("🤖 스마트 중고차 어드바이저")
    print("=" * 80)
    print()
    print(f"🚗 분석 대상:")
    print(f"  {brand} {model} {year}년 | {mileage:,}km | {fuel}")
    print(f"  💰 판매가: {sale_price:,}만원")
    print()
    print("=" * 80)
    print()
    
    # Step 1: 가격 예측
    print("📍 Step 1: AI 가격 분석")
    print("─" * 80)
    predicted_price = predict_price(brand, model, year, mileage, fuel)
    
    if not predicted_price:
        print("❌ 가격 예측 실패")
        return None
    
    price_diff = sale_price - predicted_price
    price_diff_pct = (price_diff / predicted_price * 100)
    
    print(f"  AI 예측가: {predicted_price:,.0f}만원")
    print(f"  판매가: {sale_price:,}만원")
    print(f"  차이: {price_diff:+,.0f}만원 ({price_diff_pct:+.1f}%)")
    
    if price_diff_pct > 5:
        print(f"  ⚠️ 고평가 (예측가 대비 +{price_diff_pct:.1f}%)")
    elif price_diff_pct < -5:
        print(f"  ✅ 저평가 (예측가 대비 {price_diff_pct:.1f}%)")
    else:
        print(f"  ✅ 적정가")
    
    print()
    
    # Step 2: 타이밍 분석
    print("📍 Step 2: 시장 타이밍 분석")
    print("─" * 80)
    
    data = collect_real_data_only(model)
    
    engine = RealTimingEngine()
    timing_result = engine.calculate_timing_score(
        macro_data=data['macro'],
        trend_data=data['trend'],
        schedule_data=data['schedule'],
        car_model=model
    )
    
    print(f"  타이밍 점수: {timing_result['final_score']:.1f}점/100점")
    print(f"  판단: {timing_result['color']} {timing_result['decision']}")
    print()
    
    # Step 3: Groq AI 자문 (선택)
    groq_results = {}
    
    if use_groq:
        try:
            print("📍 Step 3: Groq AI 자문")
            print("─" * 80)
            
            advisor = GroqCarAdvisor()
            
            vehicle_data = {
                'brand': brand,
                'model': model,
                'year': year,
                'mileage': mileage,
                'fuel': fuel,
                'sale_price': sale_price
            }
            
            prediction_data = {
                'predicted_price': predicted_price
            }
            
            timing_data = {
                'final_score': timing_result['final_score'],
                'decision': timing_result['decision'],
                'macro': data['macro'],
                'trend': data['trend'],
                'schedule': data['schedule']
            }
            
            # 3-1. 매수/관망 신호등
            print("\n  [1/3] 매수/관망 신호등 생성 중...")
            signal = advisor.generate_signal_report(vehicle_data, prediction_data, timing_data)
            groq_results['signal'] = signal
            
            print(f"  {signal['color']} {signal['emoji']} {signal['signal_text']} (신뢰도: {signal['confidence']}%)")
            print(f"  📝 {signal['short_summary']}")
            
            # 3-2. 허위 매물 탐지 (설명글이 있을 경우)
            if dealer_description:
                print("\n  [2/3] 허위 매물 탐지 중...")
                fraud = advisor.detect_fraud(
                    dealer_description,
                    performance_record or {}
                )
                groq_results['fraud'] = fraud
                
                if fraud['is_suspicious']:
                    print(f"  🚨 의심도: {fraud['fraud_score']}점")
                    print(f"  ⚠️ {len(fraud['warnings'])}개 경고 발견")
                else:
                    print(f"  ✅ 특이사항 없음")
            
            # 3-3. 네고 대본
            print("\n  [3/3] 네고 대본 생성 중...")
            
            issues = []
            if price_diff > 0:
                issues.append(f"시세보다 {price_diff:,.0f}만원 높음")
            if mileage > 100000:
                issues.append("주행거리 10만km 초과")
            if timing_result['final_score'] < 60:
                issues.append("시장 타이밍 좋지 않음")
            
            nego = advisor.generate_negotiation_script(
                vehicle_data,
                prediction_data,
                issues,
                style='balanced'
            )
            groq_results['negotiation'] = nego
            
            print(f"  🎯 목표가: {nego['target_price']:,}만원 (할인 {nego['discount_amount']:,}만원)")
            
            print()
            
        except Exception as e:
            print(f"  ⚠️ Groq AI 자문 실패: {e}")
            print(f"  → 데이터 분석 결과만 제공합니다")
            use_groq = False
    
    # 결과 출력
    print("=" * 80)
    print("📊 종합 분석 결과")
    print("=" * 80)
    print()
    
    # 1. 신호등
    if use_groq and 'signal' in groq_results:
        signal = groq_results['signal']
        print(f"🚦 {signal['color']} {signal['signal_text']} (신뢰도: {signal['confidence']}%)")
        print()
        print(f"📝 {signal['short_summary']}")
        print()
        print("💡 핵심 포인트:")
        for point in signal['key_points']:
            print(f"  • {point}")
        print()
        print("📊 AI 분석 리포트:")
        print(f"  {signal['report']}")
        print()
    else:
        # 기본 판단
        if price_diff_pct <= -5 and timing_result['final_score'] >= 65:
            print("🚦 🟢 매수 추천")
        elif price_diff_pct >= 5 or timing_result['final_score'] < 55:
            print("🚦 🔴 매수 회피")
        else:
            print("🚦 🟡 관망 권장")
        print()
    
    print("─" * 80)
    print()
    
    # 2. 허위 매물 경고
    if use_groq and 'fraud' in groq_results:
        fraud = groq_results['fraud']
        if fraud['is_suspicious']:
            print("🚨 허위 매물 의심")
            print(f"   의심도: {fraud['fraud_score']}점")
            print()
            print("⚠️ 경고 사항:")
            for warning in fraud['warnings']:
                print(f"  • {warning}")
            print()
            if fraud['highlighted_text']:
                print("🔍 의심스러운 문장:")
                for text in fraud['highlighted_text'][:3]:
                    print(f"  ❌ \"{text}\"")
                print()
        print("─" * 80)
        print()
    
    # 3. 네고 대본
    if use_groq and 'negotiation' in groq_results:
        nego = groq_results['negotiation']
        print("💬 네고 대본")
        print()
        print(f"🎯 목표 가격: {nego['target_price']:,}만원")
        print(f"   (현재가 {sale_price:,}만원 → 할인 {nego['discount_amount']:,}만원)")
        print()
        print("📱 문자 메시지 초안:")
        print(f'"{nego["message_script"]}"')
        print()
        print("💡 핵심 논거:")
        for arg in nego['key_arguments']:
            print(f"  • {arg}")
        print()
        print("📌 협상 팁:")
        for tip in nego['tips']:
            print(f"  • {tip}")
        print()
    
    print("=" * 80)
    
    # 결과 저장
    result = {
        'vehicle': {
            'brand': brand,
            'model': model,
            'year': year,
            'mileage': mileage,
            'fuel': fuel,
            'sale_price': sale_price
        },
        'analysis': {
            'predicted_price': predicted_price,
            'price_diff': price_diff,
            'price_diff_pct': price_diff_pct,
            'timing_score': timing_result['final_score'],
            'timing_decision': timing_result['decision']
        },
        'groq_analysis': groq_results if use_groq else None,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 파일 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"smart_analysis_{model}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"💾 결과 저장: {filename}")
    print()
    print("=" * 80)
    
    return result


def main():
    """메인 실행"""
    print("\n" + "=" * 80)
    print("🤖 스마트 중고차 어드바이저")
    print("   데이터 분석 + Groq AI 자문")
    print("=" * 80)
    print()
    
    if len(sys.argv) >= 7:
        brand = sys.argv[1]
        model = sys.argv[2]
        year = int(sys.argv[3])
        mileage = int(sys.argv[4])
        fuel = sys.argv[5]
        sale_price = int(sys.argv[6])
        
        dealer_desc = sys.argv[7] if len(sys.argv) > 7 else ""
    else:
        # 대화형 입력
        print("🚗 차량 정보를 입력하세요:")
        print()
        
        brand = input("제조사 (예: 현대): ").strip() or "현대"
        model = input("모델 (예: 그랜저): ").strip() or "그랜저"
        year = int(input("연식 (예: 2022): ").strip() or "2022")
        mileage = int(input("주행거리 (예: 35000): ").strip() or "35000")
        fuel = input("연료 (예: 가솔린): ").strip() or "가솔린"
        sale_price = int(input("판매가 (만원, 예: 3200): ").strip() or "3200")
        
        print()
        dealer_desc = input("딜러 설명글 (선택, Enter=생략): ").strip()
        
        print()
    
    # 분석 실행
    smart_analysis(
        brand=brand,
        model=model,
        year=year,
        mileage=mileage,
        fuel=fuel,
        sale_price=sale_price,
        dealer_description=dealer_desc,
        use_groq=True
    )


if __name__ == "__main__":
    main()
