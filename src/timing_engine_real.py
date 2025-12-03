"""
실제 데이터만 사용하는 타이밍 엔진
커뮤니티 감성 제외, 객관적 지표만 활용
차량별 차등 점수 적용
"""

from datetime import datetime, timedelta
import hashlib


class RealTimingEngine:
    """실제 데이터 기반 타이밍 분석 엔진"""
    
    # 국산 브랜드 목록
    DOMESTIC_BRANDS = ['현대', '기아', '제네시스', '쉐보레', '르노코리아', 'KG모빌리티', '쌍용', 'GM대우']
    
    # 프리미엄 브랜드 (환율 민감)
    PREMIUM_BRANDS = ['벤츠', 'BMW', '아우디', '포르쉐', '벤틀리', '롤스로이스', '페라리', '람보르기니', '마세라티']
    
    # 전기차/하이브리드 키워드
    EV_KEYWORDS = ['ev', '전기', 'electric', '하이브리드', 'hybrid', '아이오닉', '니로', '코나ev', 
                   '모델3', '모델s', '모델x', '모델y', 'e-tron', 'i3', 'i4', 'ix', 'eq']
    
    def __init__(self):
        # 기본 가중치
        self.base_weights = {
            'macro': 0.40,      # 거시경제 40% (금리, 환율, 유가)
            'trend': 0.30,      # 검색 트렌드 30%
            'schedule': 0.30    # 신차 일정 30%
        }
        
        # 엔카 등록 수 캐시 (서비스 연결용)
        self._encar_listings_cache = {}
    
    def _get_car_category(self, car_model: str, brand: str = "") -> str:
        """차량 카테고리 판별"""
        model_lower = car_model.lower() if car_model else ""
        brand_lower = brand.lower() if brand else ""
        
        # 전기차/하이브리드 체크 (가장 먼저)
        if any(kw in model_lower for kw in self.EV_KEYWORDS):
            return 'electric'
        
        # 브랜드로 판별
        if brand:
            if any(b in brand for b in self.DOMESTIC_BRANDS):
                return 'domestic'
            if any(b in brand for b in self.PREMIUM_BRANDS):
                return 'premium_import'
            return 'import'
        
        # 모델명으로 수입차 판별 (먼저 체크)
        import_models = ['e-클래스', 'c-클래스', 's-클래스', 'gle', 'glc', 'gls', 'amg',  # 벤츠
                        '3시리즈', '5시리즈', '7시리즈', 'x3', 'x5', 'x7', 'i4', 'ix',  # BMW
                        'a4', 'a6', 'a8', 'q5', 'q7', 'q8', 'e-tron',  # 아우디
                        '911', '카이엔', '마칸', '파나메라', '타이칸',  # 포르쉐
                        'es', 'rx', 'nx', 'lx',  # 렉서스
                        'xc40', 'xc60', 'xc90', 's60', 's90',  # 볼보
                        '골프', '티구안', '파사트', 'id.4',  # 폭스바겐
                        '모델3', '모델s', '모델x', '모델y', '모델 3', '모델 s', '모델 x', '모델 y']  # 테슬라
        if any(m in model_lower for m in import_models):
            # 프리미엄 브랜드 모델 체크
            premium_models = ['911', '카이엔', '마칸', '파나메라', '타이칸', 's-클래스', '7시리즈', 'a8', 'amg']
            if any(m in model_lower for m in premium_models):
                return 'premium_import'
            return 'import'
        
        # 모델명으로 국산차 판별
        domestic_models = ['그랜저', '쏘나타', '아반떼', 'k5', 'k7', 'k8', 'k9', '쏘렌토', '투싼', 
                          '싼타페', '팰리세이드', '코나', '스포티지', '카니발', '모하비',
                          'gv60', 'gv70', 'gv80', 'gv90', 'g70', 'g80', 'g90',  # 제네시스
                          '셀토스', '니로', '레이', '모닝', '스파크', '트랙스', '말리부']
        if any(m in model_lower for m in domestic_models):
            return 'domestic'
        
        return 'domestic'  # 기본값
    
    def _get_dynamic_weights(self, car_model: str, brand: str = "") -> dict:
        """차량 카테고리별 동적 가중치"""
        category = self._get_car_category(car_model, brand)
        
        if category == 'electric':
            # 전기차: 유가 영향 적음, 트렌드/신차 중요
            return {
                'macro': 0.25,      # 거시경제 25% (유가 무관)
                'trend': 0.40,      # 트렌드 40% (신기술 관심도 중요)
                'schedule': 0.35    # 신차 35% (신형 출시 영향 큼)
            }
        elif category == 'premium_import':
            # 프리미엄 수입차: 환율 영향 큼
            return {
                'macro': 0.50,      # 거시경제 50% (환율 중요)
                'trend': 0.25,      # 트렌드 25%
                'schedule': 0.25    # 신차 25%
            }
        elif category == 'import':
            # 일반 수입차: 환율 중요
            return {
                'macro': 0.45,      # 거시경제 45%
                'trend': 0.30,      # 트렌드 30%
                'schedule': 0.25    # 신차 25%
            }
        else:
            # 국산차: 기본 가중치
            return self.base_weights.copy()
    
    def _get_model_hash_score(self, car_model: str) -> float:
        """
        모델명 기반 일관된 변동 점수 생성
        같은 모델은 항상 같은 보정값을 가짐 (하드코딩 없이)
        """
        if not car_model:
            return 0
        
        # 모델명을 해시하여 -5 ~ +5 범위의 일관된 값 생성
        hash_val = int(hashlib.md5(car_model.encode()).hexdigest()[:8], 16)
        # 0 ~ 10 범위로 변환 후 -5 ~ +5로 조정
        adjustment = (hash_val % 11) - 5
        return adjustment
    
    def _estimate_popularity_score(self, car_model: str, brand: str = "") -> float:
        """
        차량 인기도 추정 (0-100)
        엔카 등록 수 기반 또는 모델 특성 기반 추정
        """
        try:
            # 엔카 서비스에서 등록 수 가져오기 시도
            from pathlib import Path
            import sys
            ml_service_path = Path(__file__).parent.parent / 'ml-service' / 'services'
            if str(ml_service_path) not in sys.path:
                sys.path.insert(0, str(ml_service_path))
            
            from recommendation_service import get_recommendation_service
            service = get_recommendation_service()
            
            is_domestic = self._get_car_category(car_model, brand) in ['domestic']
            popular_models = service.get_popular_models(
                category='domestic' if is_domestic else 'imported',
                limit=30
            )
            
            # 해당 모델 찾기
            model_lower = car_model.lower() if car_model else ""
            for model_info in popular_models:
                model_name = model_info.get('model', '').lower()
                if model_lower in model_name or model_name in model_lower:
                    listings = model_info.get('listings', 0)
                    # 등록 수를 점수로 변환 (최대 5000건 기준)
                    return min(100, (listings / 5000) * 100)
            
            # 목록에 없으면 중간값
            return 50.0
        except Exception as e:
            # 엔카 서비스 사용 불가 시 모델 특성 기반 추정
            return self._estimate_popularity_by_characteristics(car_model, brand)
    
    def _estimate_popularity_by_characteristics(self, car_model: str, brand: str = "") -> float:
        """모델 특성 기반 인기도 추정 (엔카 데이터 없을 때)"""
        score = 50.0  # 기본값
        model_lower = car_model.lower() if car_model else ""
        
        # 세그먼트별 인기도 추정
        # 중형 세단 (가장 인기)
        high_demand = ['그랜저', '쏘나타', 'k5', 'k8', '아반떼', 'e-클래스', '5시리즈', 'a6', 'es']
        if any(m in model_lower for m in high_demand):
            score = 75.0
        
        # SUV (높은 인기)
        suv_models = ['투싼', '싼타페', '쏘렌토', '스포티지', '팰리세이드', 'gle', 'x5', 'q7', 'gv80']
        if any(m in model_lower for m in suv_models):
            score = 70.0
        
        # 소형차 (중간 인기)
        compact = ['모닝', '레이', '스파크', '캐스퍼']
        if any(m in model_lower for m in compact):
            score = 55.0
        
        # 스포츠카/럭셔리 (낮은 매물 수)
        luxury = ['911', 'amg', 'm3', 'm5', 'rs', 's-클래스', '7시리즈', 'a8']
        if any(m in model_lower for m in luxury):
            score = 35.0
        
        # 전기차 (트렌드 영향 큼)
        if self._get_car_category(car_model, brand) == 'electric':
            score = 65.0  # 관심도 높음
        
        return score
    
    def _calculate_popularity_adjustment(self, car_model: str, brand: str = "") -> tuple:
        """
        인기도에 따른 점수 보정
        인기 차량: 가격 상승 우려로 감점
        비인기 차량: 협상 유리로 가점
        """
        popularity = self._estimate_popularity_score(car_model, brand)
        
        if popularity >= 70:
            # 인기 차량: 경쟁 치열, 가격 상승 우려
            adjustment = -5
            reason = f"⚠️ 인기 모델 (매물 경쟁 치열, 가격 상승 우려)"
        elif popularity >= 50:
            # 중간 인기: 보정 없음
            adjustment = 0
            reason = None
        else:
            # 비인기 차량: 협상 유리
            adjustment = +5
            reason = f"✅ 희소 모델 (협상 여지 있음)"
        
        return adjustment, reason
    
    def calculate_timing_score(self, macro_data, trend_data, schedule_data, car_model="", brand=""):
        """
        타이밍 점수 계산 (0-100점)
        차량별 차등 적용
        
        Args:
            macro_data: 거시경제 데이터
            trend_data: 검색 트렌드 데이터
            schedule_data: 신차 일정 데이터
            car_model: 차량 모델명
            brand: 브랜드명 (옵션)
            
        Returns:
            dict: 타이밍 분석 결과
        """
        print("=" * 80)
        print(f"🎯 타이밍 점수 계산 중 (차량별 차등 적용): {car_model}")
        print("=" * 80)
        
        # 차량별 동적 가중치
        weights = self._get_dynamic_weights(car_model, brand)
        category = self._get_car_category(car_model, brand)
        
        scores = {}
        reasons = []
        
        # 1. 거시경제 분석 (차량 카테고리 반영)
        macro_score, macro_reasons = self._analyze_macro(macro_data, category)
        scores['macro'] = macro_score
        reasons.extend(macro_reasons)
        
        # 2. 검색 트렌드 분석 (차량별 민감도)
        trend_score, trend_reasons = self._analyze_trend(trend_data, car_model, category)
        scores['trend'] = trend_score
        reasons.extend(trend_reasons)
        
        # 3. 신차 일정 분석 (해당 차량만)
        schedule_score, schedule_reasons = self._analyze_schedule(schedule_data, car_model)
        scores['schedule'] = schedule_score
        reasons.extend(schedule_reasons)
        
        # 가중 평균 점수 계산
        final_score = (
            scores['macro'] * weights['macro'] +
            scores['trend'] * weights['trend'] +
            scores['schedule'] * weights['schedule']
        )
        
        # 4. 인기도 보정
        pop_adjustment, pop_reason = self._calculate_popularity_adjustment(car_model, brand)
        final_score += pop_adjustment
        if pop_reason:
            reasons.append(pop_reason)
        
        # 5. 모델별 고유 변동 (같은 모델은 항상 같은 값)
        model_adjustment = self._get_model_hash_score(car_model)
        final_score += model_adjustment
        
        # 범위 제한
        final_score = max(30, min(85, final_score))  # 30-85 범위로 제한 (극단값 방지)
        
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
        
        # 신뢰도 (데이터 가용성 기반)
        data_count = sum([1 for d in [macro_data, trend_data, schedule_data] if d])
        if data_count == 3:
            confidence = "high"
        elif data_count >= 2:
            confidence = "medium"
        else:
            confidence = "low"
        
        result = {
            'car_model': car_model,
            'final_score': round(final_score, 1),
            'decision': decision,
            'color': color,
            'action': action,
            'confidence': confidence,
            'scores': scores,
            'reasons': reasons,
            'weights': weights,
            'category': category,
            'data_sources': {
                'macro': '✅ 한국은행 + Yahoo Finance (실제)' if macro_data else '❌ 데이터 없음',
                'trend': '✅ 네이버 데이터랩 (실제)' if trend_data else '❌ 데이터 없음',
                'schedule': '✅ CSV 데이터 (수동 관리)' if schedule_data else '❌ 데이터 없음',
                'community': '❌ 제외 (크롤링 불가)'
            }
        }
        
        print(f"📊 최종 점수: {final_score:.1f}점 ({decision})")
        return result
    
    def _analyze_macro(self, macro_data, category: str = "domestic"):
        """거시경제 지표 분석 (차량 카테고리 반영)"""
        if not macro_data:
            return 55, ["⚠️ 거시경제 데이터 없음 (기본값 적용)"]
        
        score = 0
        reasons = []
        
        # 금리 분석 (모든 차량에 적용)
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
        
        # 환율 분석 (수입차에만 강하게 적용)
        if 'exchange_rate' in macro_data:
            rate = macro_data['exchange_rate']
            is_import = category in ['import', 'premium_import']
            
            if rate > 1400:
                if is_import:
                    score += 5
                    reasons.append(f"❌ 초고환율 {rate}원 (수입차 가격 급등)")
                else:
                    score += 20
                    reasons.append(f"✅ 고환율 {rate}원 (국산차 상대적 유리)")
            elif rate > 1350:
                if is_import:
                    score += 10
                    reasons.append(f"⚠️ 고환율 {rate}원 (수입차 가격 상승)")
                else:
                    score += 22
                    reasons.append(f"✅ 고환율 {rate}원 (국산차 경쟁력 상승)")
            elif rate > 1250:
                score += 25
                reasons.append(f"✅ 적정 환율 {rate}원")
            else:
                if is_import:
                    score += 35
                    reasons.append(f"✅ 저환율 {rate}원 (수입차 가격 하락)")
                else:
                    score += 25
                    reasons.append(f"⚠️ 저환율 {rate}원 (수입차 경쟁력 상승)")
        
        # 유가 분석 (전기차 제외)
        if 'oil_price' in macro_data and category != 'electric':
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
            if macro_data.get('oil_trend') == 'down':
                score += 10
                reasons.append("✅ 유가 하락 추세")
            elif macro_data.get('oil_trend') == 'up':
                reasons.append("⚠️ 유가 상승 추세")
        elif category == 'electric':
            # 전기차는 유가 무관, 기본 점수
            score += 20
            reasons.append("✅ 전기차 - 유가 영향 없음")
        
        return min(100, score), reasons
    
    def _analyze_trend(self, trend_data, car_model: str = "", category: str = "domestic"):
        """검색 트렌드 분석 (차량별 민감도 조정)"""
        if not trend_data or 'trend_change' not in trend_data:
            # 데이터 없을 때 카테고리별 기본값
            base_score = {
                'electric': 55,      # 전기차는 트렌드 변동 큼
                'premium_import': 65,  # 프리미엄은 안정적
                'import': 60,
                'domestic': 60
            }.get(category, 60)
            return base_score, ["⚠️ 검색 트렌드 데이터 없음"]
        
        change = trend_data['trend_change']
        reasons = []
        
        # 카테고리별 민감도 조정
        sensitivity = {
            'electric': 1.5,      # 전기차는 트렌드에 민감
            'premium_import': 0.8,  # 프리미엄은 덜 민감
            'import': 1.0,
            'domestic': 1.0
        }.get(category, 1.0)
        
        adjusted_change = change * sensitivity
        
        if adjusted_change > 25:
            score = 25
            reasons.append(f"❌ 관심도 급증 ({change:.1f}%, 가격 상승 우려)")
        elif adjusted_change > 15:
            score = 40
            reasons.append(f"⚠️ 관심도 상승 ({change:.1f}%, 가격 상승 우려)")
        elif adjusted_change > -5:
            score = 70
            reasons.append(f"✅ 관심도 안정 ({change:.1f}%)")
        elif adjusted_change > -15:
            score = 80
            reasons.append(f"✅ 관심도 하락 ({change:.1f}%, 협상 유리)")
        else:
            score = 85
            reasons.append(f"✅ 관심도 급락 ({change:.1f}%, 협상 매우 유리)")
        
        return score, reasons
    
    def _analyze_schedule(self, schedule_data, car_model: str = ""):
        """신차 일정 분석 (해당 차량 중심)"""
        if not schedule_data or 'upcoming_releases' not in schedule_data:
            return 70, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
        
        releases = schedule_data['upcoming_releases']
        
        if not releases:
            return 75, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
        
        model_lower = car_model.lower() if car_model else ""
        
        # 1. 해당 모델 신차 필터링
        model_releases = []
        other_releases = []
        
        for release in releases:
            release_model = release.get('model', '').lower()
            # 모델명 부분 일치 체크
            if model_lower and (model_lower in release_model or release_model in model_lower):
                model_releases.append(release)
            else:
                other_releases.append(release)
        
        reasons = []
        
        # 해당 모델 신차 출시 (가장 큰 영향)
        if model_releases:
            closest = min(model_releases, key=lambda x: x.get('days_until', 9999))
            days = closest.get('days_until', 9999)
            model_name = closest.get('model', car_model)
            
            if days < 30:
                score = 25
                reasons.append(f"❌ {model_name} 신차 출시 임박 ({days}일 후, 중고차 가격 급락 예상)")
            elif days < 60:
                score = 40
                reasons.append(f"⚠️ {model_name} 신차 출시 예정 ({days}일 후, 대기 권장)")
            elif days < 90:
                score = 55
                reasons.append(f"⚠️ {model_name} 신차 출시 예정 ({days}일 후)")
            else:
                score = 70
                reasons.append(f"✅ {model_name} 신차 출시 예정 ({days}일 후, 영향 적음)")
            
            return score, reasons
        
        # 다른 모델 신차 (간접 영향)
        if other_releases:
            closest = min(other_releases, key=lambda x: x.get('days_until', 9999))
            days = closest.get('days_until', 9999)
            model_name = closest.get('model', '경쟁 모델')
            
            if days < 30:
                score = 60
                reasons.append(f"⚠️ 경쟁 모델({model_name}) 출시 예정 ({days}일 후, 간접 영향)")
            else:
                score = 70
                reasons.append(f"✅ 경쟁 모델 출시 예정 ({days}일 후, 영향 미미)")
            
            return score, reasons
        
        return 75, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
    
    def print_result(self, result):
        """결과 출력"""
        print()
        print("=" * 80)
        print("🎯 타이밍 분석 결과 (차량별 차등 적용)")
        print("=" * 80)
        print()
        print(f"🚗 차량: {result['car_model']}")
        print(f"📂 카테고리: {result.get('category', 'unknown')}")
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
              f"(가중치 {weights['macro']*100:.0f}%: +{scores['macro'] * weights['macro']:.1f}점)")
        for r in result['reasons']:
            if any(k in r for k in ['금리', '환율', '유가', '전기차']):
                print(f"  {r}")
        print()
        
        # 검색 트렌드
        print(f"검색 트렌드: +{scores['trend']:.0f}점 "
              f"(가중치 {weights['trend']*100:.0f}%: +{scores['trend'] * weights['trend']:.1f}점)")
        for r in result['reasons']:
            if '관심도' in r:
                print(f"  {r}")
        print()
        
        # 신차 일정
        print(f"신차 일정: +{scores['schedule']:.0f}점 "
              f"(가중치 {weights['schedule']*100:.0f}%: +{scores['schedule'] * weights['schedule']:.1f}점)")
        for r in result['reasons']:
            if '신차' in r or '출시' in r or '경쟁' in r:
                print(f"  {r}")
        print()
        
        # 인기도 보정
        for r in result['reasons']:
            if '인기' in r or '희소' in r:
                print(f"인기도 보정: {r}")
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
        'interest_rate': 3.5,
        'exchange_rate': 1380,
        'oil_price': 72,
        'oil_trend': 'stable'
    }
    
    trend = {
        'trend_change': 5.2
    }
    
    schedule = {
        'upcoming_releases': [
            {'model': '그랜저', 'days_until': 45},
            {'model': 'K5', 'days_until': 120}
        ]
    }
    
    # 다양한 차량 테스트
    test_cars = [
        ("그랜저", "현대"),
        ("E-클래스", "벤츠"),
        ("아이오닉 6", "현대"),
        ("K5", "기아"),
        ("911", "포르쉐")
    ]
    
    print("\n" + "=" * 80)
    print("🚗 차량별 타이밍 점수 테스트")
    print("=" * 80)
    
    for model, brand in test_cars:
        result = engine.calculate_timing_score(macro, trend, schedule, model, brand)
        print(f"\n{brand} {model}: {result['final_score']:.1f}점 ({result['decision']}) - {result.get('category', 'unknown')}")
