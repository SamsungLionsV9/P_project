"""
통합 API 테스트
===============
가격 예측 + 거시경제 + Groq AI 의사결정 지원 통합 테스트
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml-service'))

from services.prediction_v11 import get_prediction_service
from services.groq_service import GroqService
from services.timing import TimingService

print("="*70)
print("🚀 통합 API 테스트")
print("="*70)

# ========== 서비스 초기화 ==========
print("\n📦 서비스 초기화...")
prediction_service = get_prediction_service()
groq_service = GroqService()
timing_service = TimingService()

print(f"   ✓ 가격 예측 서비스: 로드 완료")
print(f"   ✓ Groq AI 서비스: {'사용 가능' if groq_service.is_available() else '⚠️ API 키 없음 (Fallback 모드)'}")
print(f"   ✓ 타이밍 분석 서비스: 로드 완료")

# ========== 테스트 케이스 ==========
test_cases = [
    {
        'brand': '현대',
        'model': '더 뉴 그랜저 IG',
        'year': 2022,
        'mileage': 35000,
        'options': {'has_sunroof': 1, 'has_leather_seat': 1, 'has_led_lamp': 1},
        'sale_price': 2800,  # 판매 호가
        'description': '완벽한 무사고 차량입니다. 풀옵션이며 단순 교환만 있습니다.'
    },
    {
        'brand': '벤츠',
        'model': 'E-클래스 W214',
        'year': 2022,
        'mileage': 25000,
        'options': {'has_sunroof': 1, 'has_leather_seat': 1, 'has_ventilated_seat': 1, 'has_led_lamp': 1},
        'sale_price': 6500,
        'description': '직영 인증 차량, 무사고, 신차급 관리상태'
    }
]

for i, tc in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"🧪 테스트 케이스 {i}: {tc['brand']} {tc['model']}")
    print("="*70)
    
    # ========== 1. 가격 예측 ==========
    print("\n📊 [1단계] 가격 예측")
    print("-"*50)
    
    prediction = prediction_service.predict(
        brand=tc['brand'],
        model_name=tc['model'],
        year=tc['year'],
        mileage=tc['mileage'],
        options=tc['options']
    )
    
    print(f"   예측가: {prediction.predicted_price:,.0f}만원")
    print(f"   신뢰도: {prediction.confidence:.1f}%")
    print(f"   오차범위: {prediction.price_range[0]:,.0f} ~ {prediction.price_range[1]:,.0f}만원")
    
    # 판매가 대비 분석
    sale_price = tc['sale_price']
    diff = sale_price - prediction.predicted_price
    diff_pct = (diff / prediction.predicted_price) * 100
    
    if diff_pct < -5:
        price_eval = "🟢 저평가 (좋은 가격)"
    elif diff_pct > 5:
        price_eval = "🔴 고평가 (비싼 가격)"
    else:
        price_eval = "🟡 적정가"
    
    print(f"   판매가: {sale_price:,}만원 ({diff:+,.0f}만원, {diff_pct:+.1f}%) → {price_eval}")
    
    # ========== 2. 타이밍 분석 ==========
    print(f"\n⏰ [2단계] 타이밍 분석 (거시경제 데이터)")
    print("-"*50)
    
    try:
        timing = timing_service.analyze_timing(tc['model'])
        print(f"   타이밍 점수: {timing['timing_score']:.1f}점 {timing['color']}")
        print(f"   결정: {timing['decision']}")
        print(f"   세부 점수:")
        print(f"      - 거시경제: {timing['breakdown']['macro']:.1f}점")
        print(f"      - 검색트렌드: {timing['breakdown']['trend']:.1f}점")
        print(f"      - 신차일정: {timing['breakdown']['schedule']:.1f}점")
        if timing.get('reasons'):
            print(f"   주요 이유:")
            for r in timing['reasons'][:3]:
                print(f"      {r}")
    except Exception as e:
        print(f"   ⚠️ 타이밍 분석 오류: {e}")
        timing = {'timing_score': 65, 'decision': '관망', 'color': '🟡', 
                  'breakdown': {'macro': 65, 'trend': 65, 'schedule': 65}}
    
    # ========== 3. Groq AI 분석 ==========
    print(f"\n🤖 [3단계] AI 의사결정 지원")
    print("-"*50)
    
    vehicle_data = {
        'brand': tc['brand'],
        'model': tc['model'],
        'year': tc['year'],
        'mileage': tc['mileage'],
        'sale_price': sale_price
    }
    
    prediction_data = {
        'predicted_price': prediction.predicted_price,
        'confidence': prediction.confidence,
        'mape': prediction.mape
    }
    
    timing_data = {
        'timing_score': timing['timing_score'],
        'decision': timing['decision'],
        'breakdown': timing['breakdown']
    }
    
    # 3-1. 매수/관망 신호
    signal = groq_service.generate_signal_report(vehicle_data, prediction_data, timing_data)
    print(f"\n   📍 매수 신호: {signal['emoji']} {signal['signal_text']}")
    print(f"   💬 요약: {signal['short_summary']}")
    if signal.get('key_points'):
        for kp in signal['key_points'][:3]:
            print(f"      • {kp}")
    
    # 3-2. 허위매물 탐지
    fraud = groq_service.detect_fraud(tc['description'])
    print(f"\n   🔍 허위매물 탐지:")
    print(f"      의심 점수: {fraud['fraud_score']}점")
    print(f"      의심 여부: {'⚠️ 주의 필요' if fraud['is_suspicious'] else '✅ 이상 없음'}")
    if fraud.get('warnings'):
        for w in fraud['warnings'][:2]:
            print(f"      {w}")
    
    # 3-3. 네고 대본
    nego = groq_service.generate_negotiation_script(vehicle_data, prediction_data, [])
    print(f"\n   💬 네고 추천:")
    print(f"      목표가: {nego['target_price']:,}만원")
    print(f"      할인 요청: {nego['discount_amount']:,}만원")
    print(f"\n   📱 문자 스크립트:")
    print(f"      \"{nego['message_script'][:80]}...\"")
    
    # ========== 4. 최종 의사결정 ==========
    print(f"\n🎯 [최종] 의사결정 종합")
    print("-"*50)
    
    # 종합 점수 계산
    price_score = 100 - abs(diff_pct) * 2  # 가격 적정성
    timing_score = timing['timing_score']
    final_score = (price_score * 0.5 + timing_score * 0.5)
    
    if final_score >= 75 and diff_pct <= 0:
        final_decision = "🟢 적극 구매 추천"
        final_action = "지금 바로 연락해서 네고하세요!"
    elif final_score >= 60:
        final_decision = "🟡 조건부 구매 가능"
        final_action = "네고 성공 시 구매 고려"
    else:
        final_decision = "🔴 구매 보류 권장"
        final_action = "더 좋은 매물을 기다리세요"
    
    print(f"""
   ┌────────────────────────────────────────────┐
   │  {final_decision:^38}  │
   ├────────────────────────────────────────────┤
   │  가격 적정성:  {price_score:5.1f}점                     │
   │  구매 타이밍:  {timing_score:5.1f}점                     │
   │  ─────────────────────────────             │
   │  종합 점수:    {final_score:5.1f}점                     │
   ├────────────────────────────────────────────┤
   │  💡 {final_action:<38}  │
   └────────────────────────────────────────────┘
""")

print("\n" + "="*70)
print("✅ 통합 API 테스트 완료!")
print("="*70)
