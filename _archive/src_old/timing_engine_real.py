"""
실제 데이터만 사용하는 타이밍 엔진
커뮤니티 감성 제외, 객관적 지표만 활용
"""

from datetime import datetime, timedelta


class RealTimingEngine:
    """실제 데이터 기반 타이밍 분석 엔진"""
    
    def __init__(self):
        # 가중치 (커뮤니티 제외, 3요소만)
        self.weights = {
            'macro': 0.40,      # 거시경제 40% (금리, 환율, 유가)
            'trend': 0.30,      # 검색 트렌드 30%
            'schedule': 0.30    # 신차 일정 30%
        }
    
    def calculate_timing_score(self, macro_data, trend_data, schedule_data, car_model=""):
        """
        타이밍 점수 계산 (0-100점)
        
        Args:
            macro_data: 거시경제 데이터
            trend_data: 검색 트렌드 데이터
            schedule_data: 신차 일정 데이터
            car_model: 차량 모델명
            
        Returns:
            dict: 타이밍 분석 결과
        """
        print("=" * 80)
        print("🎯 타이밍 점수 계산 중 (실제 데이터만)...")
        print("=" * 80)
        
        scores = {}
        reasons = []
        
        # 1. 거시경제 분석
        macro_score, macro_reasons = self._analyze_macro(macro_data)
        scores['macro'] = macro_score
        reasons.extend(macro_reasons)
        
        # 2. 검색 트렌드 분석
        trend_score, trend_reasons = self._analyze_trend(trend_data)
        scores['trend'] = trend_score
        reasons.extend(trend_reasons)
        
        # 3. 신차 일정 분석
        schedule_score, schedule_reasons = self._analyze_schedule(schedule_data)
        scores['schedule'] = schedule_score
        reasons.extend(schedule_reasons)
        
        # 최종 점수 계산
        final_score = (
            scores['macro'] * self.weights['macro'] +
            scores['trend'] * self.weights['trend'] +
            scores['schedule'] * self.weights['schedule']
        )
        
        # 판단
        if final_score >= 70:
            decision = "구매"
            color = "🟢"
            action = "적극 구매 추천"
        elif final_score >= 55:
            decision = "관망"
            color = "🟡"
            action = "시장 상황 지켜보기"
        else:
            decision = "대기"
            color = "🔴"
            action = "구매 시기 재고려 권장"
        
        # 신뢰도
        if all([macro_data, trend_data, schedule_data]):
            confidence = "high"
        else:
            confidence = "medium"
        
        result = {
            'car_model': car_model,
            'final_score': round(final_score, 1),
            'decision': decision,
            'color': color,
            'action': action,
            'confidence': confidence,
            'scores': scores,
            'reasons': reasons,
            'weights': self.weights,
            'data_sources': {
                'macro': '✅ 한국은행 + Yahoo Finance (실제)',
                'trend': '✅ 네이버 데이터랩 (실제)',
                'schedule': '✅ CSV 데이터 (수동 관리)',
                'community': '❌ 제외 (크롤링 불가)'
            }
        }
        
        return result
    
    def _analyze_macro(self, macro_data):
        """거시경제 지표 분석"""
        if not macro_data:
            return 50, ["⚠️ 거시경제 데이터 없음"]
        
        score = 0
        reasons = []
        
        # 금리 분석
        if 'interest_rate' in macro_data:
            rate = macro_data['interest_rate']
            if rate < 2.0:
                score += 35
                reasons.append(f"✅ 초저금리 {rate}% (구매 최적기)")
            elif rate < 3.0:
                score += 25
                reasons.append(f"✅ 저금리 {rate}% (구매 적기)")
            elif rate < 4.0:
                score += 15
                reasons.append(f"⚠️ 중금리 {rate}% (부담 증가)")
            else:
                score += 5
                reasons.append(f"❌ 고금리 {rate}% (구매 부담)")
        
        # 환율 분석
        if 'exchange_rate' in macro_data:
            rate = macro_data['exchange_rate']
            if rate > 1350:
                score += 15
                reasons.append(f"⚠️ 고환율 {rate}원 (수입차 가격 상승)")
            elif rate > 1250:
                score += 25
                reasons.append(f"✅ 적정 환율 {rate}원")
            else:
                score += 30
                reasons.append(f"✅ 저환율 {rate}원 (수입차 유리)")
        
        # 유가 분석
        if 'oil_price' in macro_data:
            oil = macro_data['oil_price']
            if oil < 60:
                score += 20
                reasons.append(f"✅ 저유가 ${oil} (유지비 감소)")
            elif oil < 80:
                score += 15
                reasons.append(f"⚠️ 보통 유가 ${oil}")
            else:
                score += 5
                reasons.append(f"❌ 고유가 ${oil} (유지비 부담)")
        
        # 유가 추세
        if 'oil_trend' in macro_data and macro_data['oil_trend'] == 'down':
            score += 10
            reasons.append("✅ 유가 하락 추세")
        elif 'oil_trend' in macro_data and macro_data['oil_trend'] == 'up':
            reasons.append("⚠️ 유가 상승 추세")
        
        return min(100, score), reasons
    
    def _analyze_trend(self, trend_data):
        """검색 트렌드 분석"""
        if not trend_data or 'trend_change' not in trend_data:
            return 50, ["⚠️ 검색 트렌드 데이터 없음"]
        
        change = trend_data['trend_change']
        reasons = []
        
        if change > 20:
            score = 30
            reasons.append(f"⚠️ 관심도 급증 ({change:.1f}%, 가격 상승 우려)")
        elif change > 10:
            score = 40
            reasons.append(f"⚠️ 관심도 상승 ({change:.1f}%, 가격 상승 우려)")
        elif change > -10:
            score = 70
            reasons.append(f"✅ 관심도 안정 ({change:.1f}%)")
        else:
            score = 85
            reasons.append(f"✅ 관심도 하락 ({change:.1f}%, 협상 유리)")
        
        return score, reasons
    
    def _analyze_schedule(self, schedule_data):
        """신차 일정 분석"""
        if not schedule_data or 'upcoming_releases' not in schedule_data:
            return 70, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
        
        releases = schedule_data['upcoming_releases']
        
        if not releases:
            return 80, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
        
        # 가장 가까운 신차 출시일
        closest_release = min(releases, key=lambda x: x.get('days_until', 9999))
        days = closest_release.get('days_until', 9999)
        
        reasons = []
        
        if days < 30:
            score = 30
            reasons.append(f"❌ 신차 출시 임박 ({days}일 후, 중고차 가격 하락 예상)")
        elif days < 60:
            score = 50
            reasons.append(f"⚠️ 신차 출시 예정 ({days}일 후, 1-2개월 대기 권장)")
        elif days < 90:
            score = 60
            reasons.append(f"⚠️ 신차 출시 예정 ({days}일 후)")
        else:
            score = 75
            reasons.append(f"✅ 신차 출시 예정 ({days}일 후, 영향 적음)")
        
        return score, reasons
    
    def print_result(self, result):
        """결과 출력"""
        print()
        print("=" * 80)
        print("🎯 타이밍 분석 결과 (실제 데이터 기반)")
        print("=" * 80)
        print()
        print(f"🚗 차량: {result['car_model']}")
        print()
        print("=" * 80)
        print(f"최종 점수: {result['final_score']:.1f}점 / 100점")
        print(f"판단: {result['color']} {result['decision']}")
        print(f"신뢰도: {result['confidence']}")
        print(f"권장 행동: {result['action']}")
        print("=" * 80)
        print()
        print("📊 세부 점수 분석:")
        print("─" * 80)
        print()
        
        scores = result['scores']
        weights = result['weights']
        
        # 거시경제
        print(f"거시경제: +{scores['macro']:.0f}점 "
              f"(가중치 적용: +{scores['macro'] * weights['macro']:.1f}점)")
        for r in result['reasons']:
            if any(k in r for k in ['금리', '환율', '유가']):
                print(f"  {r}")
        print()
        
        # 검색 트렌드
        print(f"검색 트렌드: +{scores['trend']:.0f}점 "
              f"(가중치 적용: +{scores['trend'] * weights['trend']:.1f}점)")
        for r in result['reasons']:
            if '관심도' in r:
                print(f"  {r}")
        print()
        
        # 신차 일정
        print(f"신차 일정: +{scores['schedule']:.0f}점 "
              f"(가중치 적용: +{scores['schedule'] * weights['schedule']:.1f}점)")
        for r in result['reasons']:
            if '신차' in r:
                print(f"  {r}")
        print()
        
        print("─" * 80)
        print()
        print("📌 데이터 출처:")
        for key, value in result['data_sources'].items():
            print(f"  {value}")
        print()
        print("─" * 80)
        print()
        print("🎯 권장사항:")
        if result['final_score'] >= 70:
            print("  ✅ 지금이 구매하기 좋은 시기입니다")
        elif result['final_score'] >= 55:
            print("  ⚠️ 시장 상황을 좀 더 지켜보시는 것을 권장합니다")
            print("  ⚠️ 1-2주 후 재평가 추천")
        else:
            print("  ❌ 구매 시기를 재고려하시는 것을 권장합니다")
            print("  ❌ 1-2개월 후 재평가 추천")
        print()
        print("=" * 80)


if __name__ == "__main__":
    # 테스트
    engine = RealTimingEngine()
    
    # 샘플 데이터
    macro = {
        'interest_rate': 2.5,
        'exchange_rate': 1320,
        'oil_price': 58,
        'oil_trend': 'down'
    }
    
    trend = {
        'trend_change': 5.2
    }
    
    schedule = {
        'upcoming_releases': []
    }
    
    result = engine.calculate_timing_score(macro, trend, schedule, "그랜저")
    engine.print_result(result)
