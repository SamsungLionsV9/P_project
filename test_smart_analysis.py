#!/usr/bin/env python3
"""
통합 API (smart-analysis) 종합 테스트
모든 서버 활용 및 수치 검증
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER = "test_user"

# 테스트 케이스 정의
TEST_CASES = [
    {
        "name": "국산차 - 현대 그랜저 (최신, 저주행)",
        "data": {
            "brand": "현대",
            "model": "더 뉴 그랜저 IG",
            "year": 2023,
            "mileage": 20000,
            "fuel": "가솔린",
            "has_sunroof": True,
            "has_leather_seat": True,
            "has_navigation": True,
            "is_accident_free": True,
            "inspection_grade": "good"
        },
        "expected_price_range": (2500, 3500),  # 만원 단위
    },
    {
        "name": "국산차 - 기아 K5 (중간 연식, 중간 주행)",
        "data": {
            "brand": "기아",
            "model": "K5 (DL3)",
            "year": 2021,
            "mileage": 50000,
            "fuel": "가솔린",
            "has_sunroof": False,
            "has_leather_seat": True,
            "is_accident_free": True,
            "inspection_grade": "normal"
        },
        "expected_price_range": (1800, 2500),
    },
    {
        "name": "국산차 - 제네시스 GV80 (고급, 하이브리드)",
        "data": {
            "brand": "제네시스",
            "model": "GV80 (JX1)",
            "year": 2022,
            "mileage": 30000,
            "fuel": "하이브리드",
            "has_sunroof": True,
            "has_leather_seat": True,
            "has_ventilated_seat": True,
            "has_led_lamp": True,
            "is_accident_free": True,
            "inspection_grade": "excellent"
        },
        "expected_price_range": (5000, 7000),
    },
    {
        "name": "외제차 - 벤츠 E클래스 (최신)",
        "data": {
            "brand": "벤츠",
            "model": "E-클래스",
            "year": 2022,
            "mileage": 30000,
            "fuel": "가솔린",
            "has_sunroof": True,
            "has_leather_seat": True,
            "is_accident_free": True,
            "inspection_grade": "good"
        },
        "expected_price_range": (4000, 6000),
    },
    {
        "name": "외제차 - BMW 5시리즈 (중간 연식, 디젤)",
        "data": {
            "brand": "BMW",
            "model": "5시리즈",
            "year": 2020,
            "mileage": 60000,
            "fuel": "디젤",
            "has_sunroof": True,
            "has_navigation": True,
            "is_accident_free": True,
            "inspection_grade": "normal"
        },
        "expected_price_range": (3500, 5000),
    },
    {
        "name": "외제차 - 아우디 A6 (LPG)",
        "data": {
            "brand": "아우디",
            "model": "A6",
            "year": 2021,
            "mileage": 40000,
            "fuel": "LPG",
            "has_sunroof": False,
            "is_accident_free": True,
            "inspection_grade": "normal"
        },
        "expected_price_range": (3000, 4500),
    },
    {
        "name": "국산차 - 현대 아반떼 (저가, 고주행)",
        "data": {
            "brand": "현대",
            "model": "아반떼 (CN7)",
            "year": 2019,
            "mileage": 100000,
            "fuel": "가솔린",
            "is_accident_free": False,
            "inspection_grade": "normal"
        },
        "expected_price_range": (800, 1500),
    },
]

def check_server():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ ML 서버 (8000) 정상")
            return True
    except:
        pass
    
    print("❌ ML 서버 (8000) 연결 실패")
    return False

def validate_prediction(prediction, expected_range, case_name):
    """가격 예측 결과 검증"""
    issues = []
    
    price = prediction.get("predicted_price", 0)
    price_range = prediction.get("price_range", [0, 0])
    confidence = prediction.get("confidence", 0)
    
    # 1. 가격이 합리적인 범위인지
    if price < expected_range[0] or price > expected_range[1]:
        issues.append(f"⚠️ 가격 범위 초과: {price:,.0f}만원 (예상: {expected_range[0]}-{expected_range[1]}만원)")
    
    # 2. 가격이 음수나 0이 아닌지
    if price <= 0:
        issues.append(f"❌ 가격이 0 이하: {price}")
    
    # 3. 가격 범위가 예측 가격을 포함하는지
    if price < price_range[0] or price > price_range[1]:
        issues.append(f"❌ 가격 범위 오류: 예측가 {price:,.0f}만원이 범위 [{price_range[0]:,.0f}, {price_range[1]:,.0f}] 밖")
    
    # 4. 신뢰도가 합리적인 범위인지 (50-100%)
    if confidence < 50 or confidence > 100:
        issues.append(f"⚠️ 신뢰도 범위 초과: {confidence}% (정상: 50-100%)")
    
    # 5. 가격 범위가 너무 넓지 않은지 (예측가의 ±50% 이내)
    range_width = price_range[1] - price_range[0]
    if range_width > price * 1.0:  # 예측가의 100% 이상
        issues.append(f"⚠️ 가격 범위가 너무 넓음: ±{range_width/2:,.0f}만원 (예측가의 {range_width/price*100:.1f}%)")
    
    return issues

def validate_timing(timing, case_name):
    """타이밍 분석 결과 검증"""
    issues = []
    
    if not timing:
        issues.append("❌ 타이밍 데이터 없음")
        return issues
    
    score = timing.get("timing_score", -1)
    decision = timing.get("decision", "")
    
    # 1. 타이밍 점수가 0-100 범위인지
    if score < 0 or score > 100:
        issues.append(f"❌ 타이밍 점수 범위 초과: {score} (정상: 0-100)")
    
    # 2. decision이 있는지
    if not decision:
        issues.append("⚠️ 타이밍 판단 없음")
    
    return issues

def test_case(case):
    """단일 테스트 케이스 실행"""
    print(f"\n{'='*70}")
    print(f"📋 테스트: {case['name']}")
    print(f"{'='*70}")
    
    try:
        url = f"{BASE_URL}/api/smart-analysis?user_id={TEST_USER}"
        response = requests.post(url, json=case["data"], timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text[:200]}")
            return False
        
        result = response.json()
        
        # 가격 예측 검증
        prediction = result.get("prediction", {})
        pred_issues = validate_prediction(prediction, case["expected_price_range"], case["name"])
        
        # 타이밍 검증
        timing = result.get("timing", {})
        timing_issues = validate_timing(timing, case["name"])
        
        # 결과 출력
        print(f"\n💰 가격 예측:")
        print(f"  예상 가격: {prediction.get('predicted_price', 0):,.0f}만원")
        print(f"  가격 범위: {prediction.get('price_range', [0, 0])[0]:,.0f} ~ {prediction.get('price_range', [0, 0])[1]:,.0f}만원")
        print(f"  신뢰도: {prediction.get('confidence', 0):.1f}%")
        
        if pred_issues:
            print(f"\n⚠️ 가격 예측 이슈:")
            for issue in pred_issues:
                print(f"  {issue}")
        
        print(f"\n⏱️ 타이밍 분석:")
        if timing:
            print(f"  타이밍 점수: {timing.get('timing_score', 0):.1f}점")
            print(f"  판단: {timing.get('decision', 'N/A')}")
            print(f"  라벨: {timing.get('label', 'N/A')}")
            
            if timing_issues:
                print(f"\n⚠️ 타이밍 분석 이슈:")
                for issue in timing_issues:
                    print(f"  {issue}")
        else:
            print("  ⚠️ 타이밍 데이터 없음")
        
        # Groq AI 분석 (있는 경우)
        groq = result.get("groq_analysis")
        if groq:
            print(f"\n🤖 AI 분석:")
            if groq.get("negotiation"):
                print(f"  ✅ 네고 대본 생성됨")
        
        # 전체 이슈 요약
        all_issues = pred_issues + timing_issues
        if all_issues:
            print(f"\n❌ 총 {len(all_issues)}개 이슈 발견")
            return False
        else:
            print(f"\n✅ 모든 검증 통과!")
            return True
            
    except requests.exceptions.Timeout:
        print(f"❌ 타임아웃 (30초 초과)")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    print("="*70)
    print("🧪 통합 API (smart-analysis) 종합 테스트")
    print("="*70)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"서버 URL: {BASE_URL}")
    
    # 서버 상태 확인
    if not check_server():
        print("\n❌ 서버가 실행 중이지 않습니다. 서버를 먼저 시작해주세요.")
        return
    
    # 테스트 실행
    results = []
    for case in TEST_CASES:
        success = test_case(case)
        results.append((case["name"], success))
    
    # 최종 요약
    print(f"\n\n{'='*70}")
    print("📊 테스트 결과 요약")
    print(f"{'='*70}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{status}: {name}")
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")

if __name__ == "__main__":
    main()

