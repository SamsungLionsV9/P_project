"""
Car-Sentix 타이밍 점수 엔진
실제 수집 데이터를 기반으로 0-100점 점수 계산
"""

from datetime import datetime
import json


class TimingScoreEngine:
    """타이밍 점수 계산 엔진"""
    
    def __init__(self):
        self.base_score = 50  # 기준 점수
    
    def calculate_macro_score(self, macro_data):
        """
        거시경제 지표 점수 계산
        
        Args:
            macro_data: 금리, 유가, 환율 데이터
            
        Returns:
            dict: {'score': 15, 'reasons': [...]}
        """
        score = 0
        reasons = []
        
        # 1. 금리 분석 (가중치: 높음)
        interest = macro_data.get('interest_rate', {})
        rate = interest.get('rate', 3.5)
        trend = interest.get('trend', 'stable')
        
        if rate < 2.0:
            score += 15
            reasons.append(f"✅ 초저금리 {rate}% (대출 유리)")
        elif rate < 3.0:
            score += 10
            reasons.append(f"✅ 저금리 {rate}% (구매 적기)")
        elif rate < 4.0:
            score += 5
            reasons.append(f"⚠️ 보통 금리 {rate}%")
        else:
            score -= 10
            reasons.append(f"❌ 고금리 {rate}% (대출 부담)")
        
        if trend == 'down':
            score += 5
            reasons.append("✅ 금리 하락 추세")
        elif trend == 'up':
            score -= 5
            reasons.append("⚠️ 금리 상승 추세")
        
        # 2. 유가 분석 (가중치: 중간)
        oil = macro_data.get('oil_price', {})
        price = oil.get('price', 75)
        oil_trend = oil.get('trend', 'stable')
        
        if price < 60:
            score += 5
            reasons.append(f"✅ 저유가 ${price:.0f} (유지비 감소)")
        elif price > 90:
            score -= 5
            reasons.append(f"❌ 고유가 ${price:.0f} (유지비 증가)")
        
        if oil_trend == 'down':
            score += 3
            reasons.append("✅ 유가 하락 추세")
        elif oil_trend == 'up':
            score -= 3
            reasons.append("⚠️ 유가 상승 추세")
        
        # 3. 환율 분석 (가중치: 낮음, 수입차의 경우만 영향)
        exchange = macro_data.get('exchange_rate', {})
        exch_trend = exchange.get('trend', 'stable')
        
        if exch_trend == 'down':
            score += 2
            reasons.append("✅ 환율 하락 (수입차 유리)")
        elif exch_trend == 'up':
            score -= 2
            reasons.append("⚠️ 환율 상승 (수입차 불리)")
        
        return {
            'score': score,
            'reasons': reasons,
            'weight': 0.3
        }
    
    def calculate_trend_score(self, trend_data):
        """
        검색 트렌드 점수 계산
        
        Args:
            trend_data: 네이버 검색 트렌드 데이터
            
        Returns:
            dict: {'score': 10, 'reasons': [...]}
        """
        score = 0
        reasons = []
        
        ratio = trend_data.get('ratio', 1.0)
        change_pct = trend_data.get('change_pct', 0)
        
        # 검색량 변화율 분석
        if ratio < 0.7:
            # 관심도 급락 → 인기 없음
            score -= 10
            reasons.append(f"❌ 관심도 급락 ({change_pct:.1f}%)")
        elif ratio < 0.85:
            # 관심도 하락 → 가격 하락 가능
            score += 5
            reasons.append(f"✅ 관심도 하락 ({change_pct:.1f}%, 가격 협상 유리)")
        elif ratio < 1.15:
            # 안정적
            score += 10
            reasons.append(f"✅ 안정적 관심도 ({change_pct:.1f}%)")
        elif ratio < 1.5:
            # 관심도 상승 → 가격 상승 가능
            score += 5
            reasons.append(f"⚠️ 관심도 상승 ({change_pct:.1f}%, 가격 상승 우려)")
        else:
            # 관심도 급증 → 프리미엄 발생
            score -= 5
            reasons.append(f"❌ 관심도 급증 ({change_pct:.1f}%, 프리미엄 발생)")
        
        return {
            'score': score,
            'reasons': reasons,
            'weight': 0.2
        }
    
    def calculate_sentiment_score(self, sentiment_data):
        """
        커뮤니티 감성 점수 계산
        
        Args:
            sentiment_data: 커뮤니티 감성 분석 결과
            
        Returns:
            dict: {'score': 15, 'reasons': [...]}
        """
        score = 0
        reasons = []
        
        sentiment_score = sentiment_data.get('score', 0)
        pos_ratio = sentiment_data.get('positive_ratio', 0.5)
        neg_ratio = sentiment_data.get('negative_ratio', 0.5)
        total_posts = sentiment_data.get('total_posts', 0)
        
        # 데이터 부족 시
        if total_posts < 10:
            score += 0
            reasons.append("⚠️ 커뮤니티 데이터 부족 (중립 처리)")
            return {
                'score': score,
                'reasons': reasons,
                'weight': 0.3
            }
        
        # 감성 점수 기반 분석
        if sentiment_score > 5:
            score += 15
            reasons.append(f"✅ 매우 긍정적 평가 (긍정 {pos_ratio:.0%}, 부정 {neg_ratio:.0%})")
        elif sentiment_score > 3:
            score += 10
            reasons.append(f"✅ 긍정적 평가 (긍정 {pos_ratio:.0%})")
        elif sentiment_score > -3:
            score += 5
            reasons.append(f"⚠️ 중립적 평가")
        elif sentiment_score > -5:
            score -= 10
            reasons.append(f"❌ 부정적 평가 (부정 {neg_ratio:.0%})")
        else:
            score -= 15
            reasons.append(f"❌ 매우 부정적 평가 (부정 {neg_ratio:.0%})")
        
        return {
            'score': score,
            'reasons': reasons,
            'weight': 0.3
        }
    
    def calculate_schedule_score(self, schedule_data):
        """
        신차 출시 일정 점수 계산
        
        Args:
            schedule_data: 신차 출시 일정
            
        Returns:
            dict: {'score': -10, 'reasons': [...]}
        """
        score = 0
        reasons = []
        
        has_upcoming = schedule_data.get('has_upcoming', False)
        
        if not has_upcoming:
            score += 10
            reasons.append("✅ 신차 출시 예정 없음 (중고차 가격 안정)")
            return {
                'score': score,
                'reasons': reasons,
                'weight': 0.2
            }
        
        months_until = schedule_data.get('months_until', 999)
        new_model = schedule_data.get('new_model', '')
        model_type = schedule_data.get('type', '')
        impact = schedule_data.get('impact', 'none')
        
        # 신차 출시가 가까울수록 중고차 가격 하락
        if months_until <= 2:
            score -= 15
            reasons.append(f"❌ {months_until:.1f}개월 후 신차 출시 ({new_model})")
            reasons.append("   → 중고차 가격 급락 예상, 대기 권장")
        elif months_until <= 4:
            score -= 10
            reasons.append(f"⚠️ {months_until:.1f}개월 후 신차 출시 ({new_model})")
            reasons.append("   → 가격 하락 가능, 관망 권장")
        elif months_until <= 6:
            score -= 5
            reasons.append(f"⚠️ {months_until:.1f}개월 후 신차 출시 ({new_model})")
        else:
            score += 5
            reasons.append(f"✅ 신차 출시 여유 있음 ({months_until:.1f}개월 후)")
        
        # 풀체인지는 영향 큼
        if model_type == '풀체인지':
            score -= 5
            reasons.append("⚠️ 풀체인지 모델 (큰 영향 예상)")
        
        return {
            'score': score,
            'reasons': reasons,
            'weight': 0.2
        }
    
    def calculate_final_score(self, collected_data):
        """
        최종 타이밍 점수 계산
        
        Args:
            collected_data: collect_complete_data()의 결과
            
        Returns:
            dict: {
                'final_score': 75,
                'decision': '🟢 구매 적기',
                'confidence': 'high',
                'breakdown': {...},
                'summary': [...],
                'recommendations': [...]
            }
        """
        print("\n" + "=" * 80)
        print("🎯 타이밍 점수 계산 중...")
        print("=" * 80)
        
        # 각 항목별 점수 계산
        macro_result = self.calculate_macro_score(collected_data['macro'])
        trend_result = self.calculate_trend_score(collected_data['trend'])
        sentiment_result = self.calculate_sentiment_score(
            collected_data['community']['sentiment']
        )
        schedule_result = self.calculate_schedule_score(collected_data['schedule'])
        
        # 가중 평균 점수 계산
        weighted_score = (
            macro_result['score'] * macro_result['weight'] +
            trend_result['score'] * trend_result['weight'] +
            sentiment_result['score'] * sentiment_result['weight'] +
            schedule_result['score'] * schedule_result['weight']
        )
        
        # 최종 점수 (기준 50점 + 가중 점수)
        final_score = self.base_score + weighted_score
        final_score = max(0, min(100, final_score))  # 0-100 범위 제한
        
        # 의사결정 판단
        if final_score >= 70:
            decision = "🟢 구매 적기"
            decision_text = "BUY"
            confidence = "high"
            action = "적극 구매 추천"
        elif final_score >= 55:
            decision = "🟡 관망"
            decision_text = "HOLD"
            confidence = "medium"
            action = "시장 상황 지켜보기"
        else:
            decision = "🔴 대기"
            decision_text = "WAIT"
            confidence = "high"
            action = "구매 미루기"
        
        # 결과 요약
        result = {
            'car_model': collected_data['car_model'],
            'final_score': round(final_score, 1),
            'decision': decision,
            'decision_text': decision_text,
            'confidence': confidence,
            'action': action,
            'breakdown': {
                'macro': {
                    'score': round(macro_result['score'], 1),
                    'weighted': round(macro_result['score'] * macro_result['weight'], 1),
                    'reasons': macro_result['reasons']
                },
                'trend': {
                    'score': round(trend_result['score'], 1),
                    'weighted': round(trend_result['score'] * trend_result['weight'], 1),
                    'reasons': trend_result['reasons']
                },
                'sentiment': {
                    'score': round(sentiment_result['score'], 1),
                    'weighted': round(sentiment_result['score'] * sentiment_result['weight'], 1),
                    'reasons': sentiment_result['reasons']
                },
                'schedule': {
                    'score': round(schedule_result['score'], 1),
                    'weighted': round(schedule_result['score'] * schedule_result['weight'], 1),
                    'reasons': schedule_result['reasons']
                }
            },
            'summary': self._generate_summary(macro_result, trend_result, sentiment_result, schedule_result),
            'recommendations': self._generate_recommendations(final_score, macro_result, trend_result, sentiment_result, schedule_result),
            'calculated_at': datetime.now().isoformat()
        }
        
        return result
    
    def _generate_summary(self, macro, trend, sentiment, schedule):
        """점수별 요약 생성"""
        summary = []
        
        # 각 항목의 주요 이유만 추출
        all_reasons = (
            macro['reasons'][:2] +
            trend['reasons'][:1] +
            sentiment['reasons'][:1] +
            schedule['reasons'][:2]
        )
        
        return all_reasons
    
    def _generate_recommendations(self, final_score, macro, trend, sentiment, schedule):
        """구매 의사결정 권장사항 생성"""
        recommendations = []
        
        if final_score >= 70:
            recommendations.append("✅ 지금이 구매하기 좋은 시기입니다")
            recommendations.append("✅ 금융조건이 유리하고 시장 상황이 안정적입니다")
            
            # 신차 일정 확인
            if schedule['score'] < 0:
                recommendations.append("⚠️ 다만 신차 출시를 고려하여 빠른 결정을 권장합니다")
            
        elif final_score >= 55:
            recommendations.append("⚠️ 시장 상황을 좀 더 지켜보시는 것을 권장합니다")
            recommendations.append("⚠️ 1-2주 후 재평가 추천")
            
            # 부정적 요인 체크
            if macro['score'] < 0:
                recommendations.append("⚠️ 거시경제 지표가 불리합니다")
            if sentiment['score'] < 0:
                recommendations.append("⚠️ 해당 차종에 대한 평가가 부정적입니다")
            
        else:
            recommendations.append("❌ 현재는 구매를 미루는 것이 좋습니다")
            
            # 구체적 이유
            if schedule['score'] < -10:
                recommendations.append("❌ 신차 출시 임박으로 중고차 가격 하락 예상")
            if macro['score'] < -5:
                recommendations.append("❌ 경제 상황이 구매에 불리합니다")
            if sentiment['score'] < -5:
                recommendations.append("❌ 해당 차종 평가가 매우 부정적입니다")
            
            recommendations.append("💡 1-2개월 후 재평가를 권장합니다")
        
        return recommendations
    
    def print_result(self, result):
        """결과를 보기 좋게 출력"""
        print("\n" + "=" * 80)
        print("🎯 타이밍 분석 결과")
        print("=" * 80)
        
        print(f"\n🚗 차량: {result['car_model']}")
        print(f"\n{'=' * 80}")
        print(f"최종 점수: {result['final_score']:.1f}점 / 100점")
        print(f"판단: {result['decision']}")
        print(f"신뢰도: {result['confidence']}")
        print(f"권장 행동: {result['action']}")
        print(f"{'=' * 80}")
        
        print(f"\n📊 세부 점수 분석:")
        print(f"{'─' * 80}")
        
        for category, data in result['breakdown'].items():
            category_name = {
                'macro': '거시경제',
                'trend': '검색 트렌드',
                'sentiment': '커뮤니티 감성',
                'schedule': '신차 일정'
            }[category]
            
            print(f"\n{category_name}: {data['score']:+.1f}점 (가중치 적용: {data['weighted']:+.1f}점)")
            for reason in data['reasons']:
                print(f"  {reason}")
        
        print(f"\n{'─' * 80}")
        print(f"\n💡 주요 요약:")
        for item in result['summary']:
            print(f"  {item}")
        
        print(f"\n{'─' * 80}")
        print(f"\n🎯 권장사항:")
        for rec in result['recommendations']:
            print(f"  {rec}")
        
        print(f"\n{'=' * 80}")


if __name__ == "__main__":
    # 테스트: 저장된 데이터로 점수 계산
    import glob
    
    print("=" * 80)
    print("타이밍 점수 엔진 테스트")
    print("=" * 80)
    
    # 최신 수집 데이터 파일 찾기
    data_files = glob.glob("complete_timing_data_*.json")
    
    if data_files:
        latest_file = max(data_files)
        print(f"\n📂 데이터 파일: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            collected_data = json.load(f)
        
        # 타이밍 엔진 실행
        engine = TimingScoreEngine()
        result = engine.calculate_final_score(collected_data)
        
        # 결과 출력
        engine.print_result(result)
        
        # 결과 저장
        output_file = f"timing_score_{collected_data['car_model']}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장: {output_file}")
        
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")
        print("먼저 data_collectors_complete.py를 실행하세요.")
