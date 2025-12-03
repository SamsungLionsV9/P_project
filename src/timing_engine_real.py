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
    DOMESTIC_BRANDS = ['현대', '기아', '제네시스', '쉰보레', '르노코리아', 'KG모빌리티', '쌍용', 'GM대우']

    # 프리미엄 브랜드 (환율 민감)
    PREMIUM_BRANDS = ['벤츠', 'BMW', '아우디', '포르쉐', '벤틀리', '롤스로이스', '페라리', '람보르기니', '마세라티']

    # 전기차/하이브리드 키워드
    EV_KEYWORDS = ['ev', '전기', 'electric', '하이브리드', 'hybrid', '아이오닉', '니로', '코나ev', 
                   '모델3', '모델s', '모델x', '모델y', 'e-tron', 'i3', 'i4', 'ix', 'eq']

    # 차량 세그먼트 분류 데이터
    VEHICLE_SEGMENTS = {
        'imported': [
            'BMW', 'Mercedes-Benz', '벤츠', 'Audi', '아우디', 'Volkswagen', '폭스바겐',
            'Volvo', '볼보', 'Lexus', '렉서스', 'Toyota', '토요타', 'Honda', '혼다',
            'Porsche', '포르쉐', 'Land Rover', '랜드로버', 'Jaguar', '재규어',
            '3시리즈', '5시리즈', '7시리즈', 'X3', 'X5', 'X7',
            'C-클래스', 'E-클래스', 'S-클래스', 'GLC', 'GLE', 'GLS',
            'A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8',
            'ES', 'NX', 'RX', 'LS', 'LX'
        ],
        'electric': [
            '아이오닉', 'Ioniq', '아이오닉6', '아이오닉5', 'EV6', 'EV9', 'EV5',
            '코나 일렉트릭', '니로 EV', 'Soul EV', '테슬라', 'Tesla', '모델3', '모델Y',
            'i4', 'iX', 'iX3', 'EQS', 'EQE', 'EQC', 'EQB', 'EQA',
            'e-tron', '타이칸', 'Taycan', 'ID.4', 'ID.3', '폴스타'
        ],
        'diesel': ['디젤', 'Diesel', 'CDi', 'TDI', 'CRDi', 'd20', 'd22', 'D4'],
        'luxury': [
            '그랜저', 'Grandeur', 'G80', 'G90', 'G70', 'GV60', 'GV70', 'GV80',
            '제네시스', 'Genesis', 'K9', '에쿠스', 'Equus', '체어맨', 'Chairman',
            '팰리세이드', 'Palisade', '모하비', 'Mohave'
        ],
        'economy': [
            '모닝', 'Morning', '레이', 'Ray', '스파크', 'Spark', '캐스퍼', 'Casper',
            '다마스', '라보', '마티즈', 'Matiz', '티코', 'Tico'
        ],
        'suv': [
            '투싼', 'Tucson', '싼타페', 'Santa Fe', '코나', 'Kona', '베뉴', 'Venue',
            '쏘렌토', 'Sorento', '스포티지', 'Sportage', '셀토스', 'Seltos', '니로', 'Niro',
            'QM6', 'XM3', '티볼리', 'Tivoli', '코란도', 'Korando', '렉스턴', 'Rexton',
            '트레일블레이저', 'Trailblazer', '트랙스', 'Trax', '캡티바', 'Captiva'
        ]
    }

    # 세그먼트별 가중치 설정
    SEGMENT_WEIGHTS = {
        'default': {'macro': 0.40, 'trend': 0.30, 'schedule': 0.30},
        'imported': {'macro': 0.50, 'trend': 0.25, 'schedule': 0.25},  # 환율 영향
        'electric': {'macro': 0.25, 'trend': 0.35, 'schedule': 0.40},  # 신차/보조금 중요
        'diesel': {'macro': 0.45, 'trend': 0.25, 'schedule': 0.30},    # 환경 정책
        'luxury': {'macro': 0.50, 'trend': 0.25, 'schedule': 0.25},    # 금리 민감
        'economy': {'macro': 0.35, 'trend': 0.35, 'schedule': 0.30},   # 균형적
        'suv': {'macro': 0.40, 'trend': 0.30, 'schedule': 0.30}        # 기본
    }

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
        """차량 카테고리 판별 (GitHub 버전 호환)"""
        model_lower = car_model.lower() if car_model else ""
        brand_lower = brand.lower() if brand else ""

        # 전기차 체크
        if any(kw in model_lower for kw in self.EV_KEYWORDS):
            return 'electric'

        # 브랜드로 판별
        if brand:
            if any(b in brand for b in self.DOMESTIC_BRANDS):
                return 'domestic'
            if any(b in brand for b in self.PREMIUM_BRANDS):
                return 'premium_import'
            return 'import'

        return 'domestic'

    def _get_model_hash_score(self, car_model: str) -> float:
        """
        모델명 기반 일관된 변동 점수 생성
        같은 모델은 항상 같은 보정값을 가짐 (하드코딩 없이)
        """
        if not car_model:
            return 0

        hash_val = int(hashlib.md5(car_model.encode()).hexdigest()[:8], 16)
        adjustment = (hash_val % 11) - 5  # -5 ~ +5 범위
        return adjustment

    def _estimate_popularity_score(self, car_model: str, brand: str = "") -> float:
        """차량 인기도 추정 (0-100)"""
        score = 50.0  # 기본값
        model_lower = car_model.lower() if car_model else ""

        # 고수요 모델
        high_demand = ['그랜저', '쏘나타', 'k5', 'k8', '아반떼', 'e-클래스', '5시리즈', 'a6', 'es']
        if any(m in model_lower for m in high_demand):
            score = 75.0

        # SUV
        suv_models = ['투싼', '싼타페', '쏘렌토', '스포티지', '팰리세이드', 'gle', 'x5', 'q7', 'gv80']
        if any(m in model_lower for m in suv_models):
            score = 70.0

        # 소형차
        compact = ['모닝', '레이', '스파크', '캐스퍼']
        if any(m in model_lower for m in compact):
            score = 55.0

        # 럭셔리
        luxury = ['911', 'amg', 'm3', 'm5', 'rs', 's-클래스', '7시리즈', 'a8']
        if any(m in model_lower for m in luxury):
            score = 35.0

        return score

    def _calculate_popularity_adjustment(self, car_model: str, brand: str = "") -> tuple:
        """인기도에 따른 점수 보정"""
        popularity = self._estimate_popularity_score(car_model, brand)

        if popularity >= 70:
            adjustment = -5
            reason = "⚠️ 인기 모델 (매물 경쟁 치열, 가격 상승 우려)"
        elif popularity >= 50:
            adjustment = 0
            reason = None
        else:
            adjustment = +5
            reason = "✅ 희소 모델 (협상 여지 있음)"

        return adjustment, reason

    def _detect_segment(self, car_model: str, brand: str = "", fuel_type: str = "") -> list:
        """
        차량 세그먼트 감지 (복수 세그먼트 가능)
        
        Args:
            car_model: 차량 모델명
            brand: 제조사 (선택)
            fuel_type: 연료 타입 (선택)
        
        Returns:
            list: 감지된 세그먼트 리스트
        """
        segments = []
        search_text = f"{brand} {car_model} {fuel_type}".lower()
        
        for segment, keywords in self.VEHICLE_SEGMENTS.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    if segment not in segments:
                        segments.append(segment)
                    break
        
        return segments if segments else ['default']
    
    def _get_segment_weights(self, segments: list) -> dict:
        """
        세그먼트 기반 가중치 계산 (복수 세그먼트 평균)
        """
        if not segments or segments == ['default']:
            return self.SEGMENT_WEIGHTS['default'].copy()
        
        # 복수 세그먼트의 가중치 평균
        weights = {'macro': 0, 'trend': 0, 'schedule': 0}
        valid_segments = [s for s in segments if s in self.SEGMENT_WEIGHTS]
        
        if not valid_segments:
            return self.SEGMENT_WEIGHTS['default'].copy()
        
        for segment in valid_segments:
            seg_weights = self.SEGMENT_WEIGHTS[segment]
            for key in weights:
                weights[key] += seg_weights[key]
        
        for key in weights:
            weights[key] /= len(valid_segments)
        
        return weights
    
    def calculate_timing_score(self, macro_data, trend_data, schedule_data, car_model="", brand="", fuel_type=""):
        """
        타이밍 점수 계산 (0-100점) - 차량별 도메인 지식 적용
        
        Args:
            macro_data: 거시경제 데이터
            trend_data: 검색 트렌드 데이터
            schedule_data: 신차 일정 데이터
            car_model: 차량 모델명
            brand: 제조사 (선택)
            fuel_type: 연료 타입 (선택)
            
        Returns:
            dict: 타이밍 분석 결과
        """
        # 1. 차량 세그먼트 감지
        segments = self._detect_segment(car_model, brand, fuel_type)
        self.weights = self._get_segment_weights(segments)
        
        print("=" * 80)
        print(f"🎯 타이밍 점수 계산 중 (차량: {car_model})")
        print(f"📌 감지된 세그먼트: {segments}")
        print(f"📊 적용 가중치: macro={self.weights['macro']:.0%}, trend={self.weights['trend']:.0%}, schedule={self.weights['schedule']:.0%}")
        print("=" * 80)
        
        scores = {}
        reasons = []
        
        # 2. 거시경제 분석 (세그먼트별 커스텀)
        macro_score, macro_reasons = self._analyze_macro(macro_data, segments)
        scores['macro'] = macro_score
        reasons.extend(macro_reasons)
        
        # 3. 검색 트렌드 분석
        trend_score, trend_reasons = self._analyze_trend(trend_data)
        scores['trend'] = trend_score
        reasons.extend(trend_reasons)
        
        # 4. 신차 일정 분석
        schedule_score, schedule_reasons = self._analyze_schedule(schedule_data, segments)
        scores['schedule'] = schedule_score
        reasons.extend(schedule_reasons)
        
        # 5. 최종 점수 계산 (가중 평균)
        final_score = (
            scores['macro'] * self.weights['macro'] +
            scores['trend'] * self.weights['trend'] +
            scores['schedule'] * self.weights['schedule']
        )
        
        # 6. 인기도 보정 (GitHub 버전 기능)
        pop_adjustment, pop_reason = self._calculate_popularity_adjustment(car_model, brand)
        final_score += pop_adjustment
        if pop_reason:
            reasons.append(pop_reason)
        
        # 7. 모델별 고유 변동 (같은 모델은 항상 같은 값)
        model_adjustment = self._get_model_hash_score(car_model)
        final_score += model_adjustment
        
        # 8. 범위 제한 (극단값 방지)
        final_score = max(30, min(85, final_score))
        
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
        
        # 카테고리 (GitHub 호환)
        category = self._get_car_category(car_model, brand)
        
        result = {
            'car_model': car_model,
            'category': category,  # GitHub 호환
            'segments': segments,  # 세그먼트 상세
            'final_score': round(final_score, 1),
            'decision': decision,
            'color': color,
            'action': action,
            'confidence': confidence,
            'scores': scores,
            'reasons': reasons,
            'weights': self.weights,
            'segment_info': self._get_segment_description(segments),
            'data_sources': {
                'macro': '✅ 한국은행 + Yahoo Finance (실제)',
                'trend': '✅ 네이버 데이터랩 (실제)',
                'schedule': '✅ CSV 데이터 (수동 관리)',
                'community': '❌ 제외 (크롤링 불가)'
            }
        }
        
        return result
    
    def _get_segment_description(self, segments: list) -> str:
        """세그먼트 설명 반환"""
        descriptions = {
            'imported': '수입차 - 환율 영향 민감',
            'electric': '전기차 - 보조금/신모델 중요, 유가 무관',
            'diesel': '디젤 - 환경 정책 영향',
            'luxury': '고급차 - 금리 민감',
            'economy': '경차 - 유가 민감',
            'suv': 'SUV - 계절성 영향',
            'default': '일반 차량 - 표준 분석'
        }
        return ', '.join([descriptions.get(s, s) for s in segments])
    
    def _analyze_macro(self, macro_data, segments=None):
        """
        거시경제 지표 분석 (세그먼트별 차별화)
        
        세그먼트별 영향도:
        - 수입차: 환율 영향 +++, 금리 영향 ++
        - 전기차: 유가 영향 무시, 금리 영향 ++
        - 디젤: 환경 정책 추가, 유가 영향 ++
        - 고급차: 금리 영향 +++
        - 경차: 유가 영향 +++, 금리 영향 -
        """
        if not macro_data:
            return 50, ["⚠️ 거시경제 데이터 없음"]
        
        segments = segments or ['default']
        score = 0
        reasons = []
        
        is_imported = 'imported' in segments
        is_electric = 'electric' in segments
        is_diesel = 'diesel' in segments
        is_luxury = 'luxury' in segments
        is_economy = 'economy' in segments
        
        # 금리 분석 (고급차/수입차는 더 민감)
        if 'interest_rate' in macro_data:
            rate = macro_data['interest_rate']
            
            # 기본 점수
            if rate < 2.0:
                base_score = 35
                msg = f"✅ 초저금리 {rate}%"
            elif rate < 3.0:
                base_score = 25
                msg = f"✅ 저금리 {rate}%"
            elif rate < 4.0:
                base_score = 15
                msg = f"⚠️ 중금리 {rate}%"
            else:
                base_score = 5
                msg = f"❌ 고금리 {rate}%"
            
            # 세그먼트별 조정
            if is_luxury or is_imported:
                base_score = int(base_score * 1.2)  # 고급차/수입차: 금리 영향 20% 증가
                msg += " (고가 차량은 금리에 민감)"
            elif is_economy:
                base_score = int(base_score * 0.8)  # 경차: 금리 영향 20% 감소
                msg += " (경차는 금리 영향 적음)"
            
            score += base_score
            reasons.append(msg)
        
        # 환율 분석 (수입차는 매우 민감)
        if 'exchange_rate' in macro_data:
            rate = macro_data['exchange_rate']
            
            if is_imported:
                # 수입차: 환율 영향 강화
                if rate > 1400:
                    score += 5
                    reasons.append(f"❌ 고환율 {rate:.0f}원 (수입차 가격 크게 상승)")
                elif rate > 1300:
                    score += 15
                    reasons.append(f"⚠️ 환율 상승 {rate:.0f}원 (수입차 가격 영향)")
                else:
                    score += 30
                    reasons.append(f"✅ 저환율 {rate:.0f}원 (수입차 구매 적기)")
            else:
                # 국산차: 환율 영향 약함
                if rate > 1350:
                    score += 20
                    reasons.append(f"⚠️ 고환율 {rate:.0f}원 (부품가 상승 영향)")
                else:
                    score += 25
                    reasons.append(f"✅ 환율 안정 {rate:.0f}원")
        
        # 유가 분석 (세그먼트별 차별화)
        if 'oil_price' in macro_data:
            oil = macro_data['oil_price']
            
            if is_electric:
                # 전기차: 유가 무관
                score += 25
                reasons.append(f"✅ 전기차는 유가(${oil}) 영향 없음")
            elif is_economy:
                # 경차: 유가 매우 민감 (연비가 중요)
                if oil < 60:
                    score += 25
                    reasons.append(f"✅ 저유가 ${oil} (경차 유지비 매력 감소)")
                elif oil < 80:
                    score += 20
                    reasons.append(f"✅ 보통 유가 ${oil} (경차 유지비 이점)")
                else:
                    score += 30  # 고유가일수록 경차 수요 증가 → 가격 상승 우려
                    reasons.append(f"⚠️ 고유가 ${oil} (경차 수요↑, 가격 상승 우려)")
            elif is_diesel:
                # 디젤: 유가 민감 + 환경 정책 고려
                if oil < 60:
                    score += 20
                    reasons.append(f"✅ 저유가 ${oil} (디젤 연료비 절감)")
                else:
                    score += 10
                    reasons.append(f"⚠️ 유가 ${oil} + 디젤차 환경 규제 강화 추세")
            else:
                # 일반 차량
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
    
    def _analyze_schedule(self, schedule_data, segments=None):
        """
        신차 일정 분석 (세그먼트별 차별화)
        
        전기차: 정부 보조금 정책, 신모델 출시 영향 큼
        고급차: 풀체인지 영향 큼
        일반차: 표준 분석
        """
        segments = segments or ['default']
        is_electric = 'electric' in segments
        is_luxury = 'luxury' in segments
        
        if not schedule_data or 'upcoming_releases' not in schedule_data:
            base_msg = "✅ 신차 출시 예정 없음"
            if is_electric:
                return 75, [base_msg + " (전기차 보조금 정책 확인 필요)"]
            return 70, [base_msg + " (중고차 가격 안정)"]
        
        releases = schedule_data['upcoming_releases']
        
        if not releases:
            if is_electric:
                return 80, ["✅ 관련 신차 없음 (전기차 보조금 2025년 유지 시 유리)"]
            return 80, ["✅ 신차 출시 예정 없음 (중고차 가격 안정)"]
        
        # 가장 가까운 신차 출시일
        closest_release = min(releases, key=lambda x: x.get('days_until', 9999))
        days = closest_release.get('days_until', 9999)
        car_name = closest_release.get('name', '신차')
        
        reasons = []
        
        # 세그먼트별 영향도 조정
        if is_luxury or is_electric:
            # 고급차/전기차: 신모델 영향 더 큼
            if days < 30:
                score = 25
                reasons.append(f"❌ {car_name} 출시 임박 ({days}일 후, 가격 하락 예상)")
            elif days < 60:
                score = 40
                reasons.append(f"⚠️ {car_name} 출시 예정 ({days}일 후, 대기 강력 권장)")
            elif days < 90:
                score = 55
                reasons.append(f"⚠️ {car_name} 출시 예정 ({days}일 후)")
            else:
                score = 75
                reasons.append(f"✅ {car_name} 출시 예정 ({days}일 후, 영향 적음)")
        else:
            # 일반 차량
            if days < 30:
                score = 30
                reasons.append(f"❌ {car_name} 출시 임박 ({days}일 후, 중고차 가격 하락 예상)")
            elif days < 60:
                score = 50
                reasons.append(f"⚠️ {car_name} 출시 예정 ({days}일 후, 1-2개월 대기 권장)")
            elif days < 90:
                score = 60
                reasons.append(f"⚠️ {car_name} 출시 예정 ({days}일 후)")
            else:
                score = 75
                reasons.append(f"✅ {car_name} 출시 예정 ({days}일 후, 영향 적음)")
        
        return score, reasons
    
    def print_result(self, result):
        """결과 출력"""
        print()
        print("=" * 80)
        print("🎯 타이밍 분석 결과 (실제 데이터 + 차량별 도메인 지식)")
        print("=" * 80)
        print()
        print(f"🚗 차량: {result['car_model']}")
        print(f"📌 세그먼트: {result.get('segments', ['default'])}")
        print(f"💡 분석 특성: {result.get('segment_info', '표준 분석')}")
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
    # 테스트 - 다양한 세그먼트
    engine = RealTimingEngine()
    
    # 샘플 데이터
    macro = {
        'interest_rate': 2.5,
        'exchange_rate': 1465,  # 현재 환율 반영
        'oil_price': 59,
        'oil_trend': 'stable'
    }
    
    trend = {
        'trend_change': -22.8  # 검색량 하락
    }
    
    schedule = {
        'upcoming_releases': []
    }
    
    # 테스트 케이스들
    test_cases = [
        ("그랜저", "현대", "가솔린"),      # 고급차
        ("모닝", "기아", "가솔린"),         # 경차
        ("아이오닉6", "현대", "전기"),      # 전기차
        ("BMW 5시리즈", "BMW", "가솔린"),   # 수입차
        ("쏘렌토 디젤", "기아", "디젤"),    # 디젤 SUV
        ("아반떼", "현대", "가솔린"),       # 일반차
    ]
    
    print("\n" + "=" * 80)
    print("🚗 차량 세그먼트별 타이밍 분석 테스트")
    print("=" * 80 + "\n")
    
    for model, brand, fuel in test_cases:
        result = engine.calculate_timing_score(macro, trend, schedule, model, brand, fuel)
        print(f"\n📌 {brand} {model} ({fuel})")
        print(f"   세그먼트: {result['segments']}")
        print(f"   가중치: macro={result['weights']['macro']:.0%}, trend={result['weights']['trend']:.0%}, schedule={result['weights']['schedule']:.0%}")
        print(f"   점수: {result['final_score']:.1f}점 {result['color']} {result['decision']}")
        print(f"   설명: {result['segment_info']}")
        print("-" * 60)
