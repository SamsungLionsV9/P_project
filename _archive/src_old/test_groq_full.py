"""
Groq AI 전체 기능 테스트
"""

from groq_advisor import GroqCarAdvisor

print("=" * 80)
print("🧪 Groq AI 전체 기능 테스트")
print("=" * 80)
print()

try:
    advisor = GroqCarAdvisor()
    
    # 테스트 데이터
    vehicle = {
        'brand': '현대',
        'model': '그랜저',
        'year': 2022,
        'mileage': 35000,
        'fuel': '가솔린',
        'sale_price': 3200
    }
    
    prediction = {
        'predicted_price': 2980
    }
    
    timing = {
        'final_score': 64.0,
        'decision': '관망',
        'macro': {'interest_rate': 2.5, 'oil_price': 58},
        'trend': {'trend_change': 5.2},
        'schedule': {'upcoming_releases': []}
    }
    
    # 1️⃣ 매수/관망 신호등
    print("1️⃣ 매수/관망 신호등")
    print("─" * 80)
    signal = advisor.generate_signal_report(vehicle, prediction, timing)
    print(f"\n{signal['color']} {signal['emoji']} {signal['signal_text']} (신뢰도: {signal['confidence']}%)")
    print(f"\n📝 {signal['short_summary']}")
    print(f"\n💡 핵심 포인트:")
    for point in signal['key_points']:
        print(f"  • {point}")
    print(f"\n📊 상세 리포트:")
    print(f"  {signal['report']}")
    
    print("\n" + "=" * 80)
    print()
    
    # 2️⃣ 허위 매물 탐지
    print("2️⃣ 허위 매물 탐지")
    print("─" * 80)
    
    dealer_desc = """
    완전 무사고 차량입니다. 상태 최상!
    타이어 미세한 마모 있지만 새차급 컨디션입니다.
    오일은 조금 누유되지만 주행에 지장 없습니다.
    """
    
    performance = {
        'accidents': '프론트 범퍼 교체',
        'repairs': '엔진 오일 누유 수리 이력',
        'replacements': '타이어 4개 교체 필요'
    }
    
    fraud = advisor.detect_fraud(dealer_desc, performance)
    
    if fraud['is_suspicious']:
        print(f"\n🚨 허위 매물 의심")
        print(f"   의심도: {fraud['fraud_score']}점")
        print(f"\n⚠️ 경고 사항:")
        for warning in fraud['warnings'][:5]:
            print(f"  • {warning}")
        
        if fraud['highlighted_text']:
            print(f"\n🔍 의심스러운 문장:")
            for text in fraud['highlighted_text'][:3]:
                print(f"  ❌ \"{text}\"")
        
        print(f"\n📝 종합 의견:")
        print(f"  {fraud['summary']}")
    else:
        print(f"\n✅ 특이사항 없음")
        print(f"   {fraud['summary']}")
    
    print("\n" + "=" * 80)
    print()
    
    # 3️⃣ 네고 대본 생성
    print("3️⃣ 네고 대본 생성")
    print("─" * 80)
    
    issues = [
        "시세보다 220만원 높음",
        "타이어 교체 필요 (약 80만원)",
        "오일 누유 수리 필요"
    ]
    
    nego = advisor.generate_negotiation_script(
        vehicle,
        prediction,
        issues,
        style='balanced'
    )
    
    print(f"\n🎯 목표 가격: {nego['target_price']:,}만원")
    print(f"   (현재가 {vehicle['sale_price']:,}만원 → 할인 {nego['discount_amount']:,}만원)")
    
    print(f"\n📱 문자 메시지 초안:")
    print(f'"{nego["message_script"]}"')
    
    print(f"\n☎️ 전화 통화 대본:")
    print(f'"{nego["phone_script"]}"')
    
    print(f"\n💡 핵심 논거:")
    for arg in nego['key_arguments']:
        print(f"  • {arg}")
    
    print(f"\n📌 협상 팁:")
    for tip in nego['tips']:
        print(f"  • {tip}")
    
    print("\n" + "=" * 80)
    print()
    print("✅ 모든 테스트 성공!")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
