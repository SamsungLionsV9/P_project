"""
타이밍 분석 서비스
거시경제, 검색 트렌드, 신차 일정을 분석하여 구매 타이밍 판단
차량별 차등 점수 적용
"""

import sys
import os
import hashlib
from pathlib import Path
from typing import Dict

# 1. 같은 폴더의 data_collectors 사용
try:
    from .data_collectors import collect_real_data_only
except ImportError:
    # 2. Fallback: src 폴더에서
    src_path = Path(__file__).parent.parent.parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from data_collectors_real_only import collect_real_data_only
    except ImportError as e:
        collect_real_data_only = None

# timing_engine은 src에서 가져옴
try:
    src_path = Path(__file__).parent.parent.parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from timing_engine_real import RealTimingEngine
except ImportError as e:
    RealTimingEngine = None


class TimingService:
    """타이밍 분석 서비스"""
    
    # 국산 브랜드 목록
    DOMESTIC_BRANDS = ['현대', '기아', '제네시스', '쉐보레', '르노코리아', 'KG모빌리티', '쌍용']
    
    # 전기차/하이브리드 키워드
    EV_KEYWORDS = ['ev', '전기', 'electric', '하이브리드', 'hybrid', '아이오닉', '니로', '코나ev',
                   '모델3', '모델s', '모델x', '모델y', 'e-tron', 'i3', 'i4', 'ix', 'eq']
    
    def __init__(self):
        if RealTimingEngine:
            self.timing_engine = RealTimingEngine()
        else:
            self.timing_engine = None
    
    def analyze_timing(self, car_model: str, brand: str = "") -> Dict:
        """
        타이밍 분석
        
        Args:
            car_model: 차량 모델명
            brand: 브랜드명 (옵션)
            
        Returns:
            dict: {
                'timing_score': float (0-100),
                'decision': str (구매/관망/대기),
                'color': str,
                'breakdown': dict,
                'reasons': list,
                'data_available': bool
            }
        """
        if not self.timing_engine or not collect_real_data_only:
            return self._fallback_timing_analysis(car_model, brand)
        
        try:
            # 실제 데이터 수집
            data = collect_real_data_only(car_model)
            
            # 타이밍 점수 계산 (브랜드 정보 전달)
            result = self.timing_engine.calculate_timing_score(
                macro_data=data['macro'],
                trend_data=data['trend'],
                schedule_data=data['schedule'],
                car_model=car_model,
                brand=brand
            )
            
            # API 응답 형식으로 변환
            score = float(result['final_score'])
            decision = result['decision']
            
            # 앱 호환 label
            label = self._get_label(score, decision)
            
            # 앱 호환 factors
            factors = self._convert_reasons_to_factors(result.get('reasons', []))
            
            return {
                'timing_score': score,
                'decision': decision,
                'label': label,
                'color': result['color'],
                'breakdown': {
                    'macro': float(result['scores']['macro']),
                    'trend': float(result['scores']['trend']),
                    'schedule': float(result['scores']['schedule'])
                },
                'reasons': result['reasons'],
                'factors': factors,
                'action': result['action'],
                'confidence': result['confidence'],
                'category': result.get('category', 'unknown'),
                'data_available': True
            }
            
        except Exception as e:
            print(f"⚠️ 타이밍 분석 중 오류: {e}")
            return self._fallback_timing_analysis(car_model, brand)
    
    def _get_label(self, score: float, decision: str) -> str:
        """타이밍 점수에 따른 라벨 반환"""
        if score >= 70:
            return "적극 매수"
        elif score >= 55:
            return "매수 추천"
        elif score >= 45:
            return "보통"
        else:
            return "대기 권장"
    
    def _convert_reasons_to_factors(self, reasons: list) -> list:
        """reasons 리스트를 앱 호환 factors 형식으로 변환"""
        factors = []
        for reason in reasons:
            # 이모지와 키워드로 상태 판단
            clean_reason = reason.replace('✅ ', '').replace('⚠️ ', '').replace('❌ ', '').replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')
            
            if '✅' in reason or '🟢' in reason or '좋' in reason or '추천' in reason or '유리' in reason:
                status = 'positive'
            elif '❌' in reason or '🔴' in reason or '주의' in reason or '하락' in reason or '위험' in reason or '부담' in reason or '급등' in reason:
                status = 'negative'
            else:
                status = 'neutral'
            
            factors.append({
                'factor': 'timing',
                'status': status,
                'description': clean_reason
            })
        return factors
    
    def _get_car_category(self, car_model: str, brand: str = "") -> str:
        """차량 카테고리 판별"""
        model_lower = car_model.lower() if car_model else ""
        
        # 전기차/하이브리드 체크 (가장 먼저)
        if any(kw in model_lower for kw in self.EV_KEYWORDS):
            return 'electric'
        
        # 브랜드로 판별
        if brand:
            if any(b in brand for b in self.DOMESTIC_BRANDS):
                return 'domestic'
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
            return 'import'
        
        # 모델명으로 국산차 판별
        domestic_models = ['그랜저', '쏘나타', '아반떼', 'k5', 'k7', 'k8', 'k9', '쏘렌토', '투싼',
                          '싼타페', '팰리세이드', '코나', '스포티지', '카니발', '모하비',
                          'gv60', 'gv70', 'gv80', 'gv90', 'g70', 'g80', 'g90',  # 제네시스
                          '셀토스', '니로', '레이', '모닝', '스파크', '트랙스', '말리부']
        if any(m in model_lower for m in domestic_models):
            return 'domestic'
        
        return 'domestic'  # 기본값
    
    def _get_model_hash_score(self, car_model: str) -> float:
        """모델명 기반 일관된 변동 점수 생성"""
        if not car_model:
            return 0
        hash_val = int(hashlib.md5(car_model.encode()).hexdigest()[:8], 16)
        adjustment = (hash_val % 11) - 5  # -5 ~ +5
        return adjustment
    
    def _estimate_base_score(self, car_model: str, brand: str = "") -> tuple:
        """차량 특성 기반 기본 점수 추정"""
        category = self._get_car_category(car_model, brand)
        model_lower = car_model.lower() if car_model else ""
        
        # 카테고리별 기본 점수
        base_scores = {
            'electric': {
                'macro': 60,   # 전기차는 유가 영향 없음
                'trend': 55,   # 트렌드 변동 큼
                'schedule': 60  # 신차 출시 빈번
            },
            'import': {
                'macro': 55,   # 환율 영향
                'trend': 65,   # 상대적 안정
                'schedule': 70  # 신차 영향 적음
            },
            'domestic': {
                'macro': 60,   # 기본값
                'trend': 60,
                'schedule': 65
            }
        }
        
        scores = base_scores.get(category, base_scores['domestic']).copy()
        reasons = []
        
        # 세그먼트별 조정
        # 인기 모델 (경쟁 치열)
        popular_models = ['그랜저', '쏘나타', 'k5', '투싼', '싼타페', '쏘렌토', 'e-클래스', '5시리즈']
        if any(m in model_lower for m in popular_models):
            scores['trend'] -= 5
            reasons.append("⚠️ 인기 모델 (매물 경쟁 치열)")
        
        # 비인기/희소 모델 (협상 유리)
        rare_models = ['911', 'amg', 'm3', 'm5', 'rs', '마세라티', '벤틀리']
        if any(m in model_lower for m in rare_models):
            scores['trend'] += 5
            reasons.append("✅ 희소 모델 (협상 여지 있음)")
        
        # SUV 프리미엄
        suv_keywords = ['투싼', '싼타페', '쏘렌토', '스포티지', '팰리세이드', 'gle', 'x5', 'q7', 'gv80']
        if any(m in model_lower for m in suv_keywords):
            scores['schedule'] -= 3  # SUV는 신차 경쟁 치열
            reasons.append("⚠️ SUV 세그먼트 (신차 경쟁 치열)")
        
        return scores, reasons, category
    
    def _fallback_timing_analysis(self, car_model: str, brand: str = "") -> Dict:
        """
        Fallback 타이밍 분석 (데이터 수집 실패 시)
        차량별 차등 점수 적용
        
        Args:
            car_model: 차량 모델명
            brand: 브랜드명
            
        Returns:
            dict: 차량별 차등 타이밍 분석 결과
        """
        # 차량 특성 기반 점수 추정
        scores, category_reasons, category = self._estimate_base_score(car_model, brand)
        
        # 가중치 (카테고리별)
        if category == 'electric':
            weights = {'macro': 0.25, 'trend': 0.40, 'schedule': 0.35}
        elif category == 'import':
            weights = {'macro': 0.45, 'trend': 0.30, 'schedule': 0.25}
        else:
            weights = {'macro': 0.40, 'trend': 0.30, 'schedule': 0.30}
        
        # 가중 평균 계산
        final_score = (
            scores['macro'] * weights['macro'] +
            scores['trend'] * weights['trend'] +
            scores['schedule'] * weights['schedule']
        )
        
        # 모델별 고유 변동 적용
        model_adjustment = self._get_model_hash_score(car_model)
        final_score += model_adjustment
        
        # 범위 제한 (45-75)
        final_score = max(45, min(75, final_score))
        
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
        
        # 이유 생성
        reasons = [
            "⚠️ 실시간 데이터를 불러올 수 없습니다",
            f"⚠️ {category.upper()} 차량 특성 기반 분석 제공"
        ]
        reasons.extend(category_reasons)
        
        # 반환
        return {
            'timing_score': round(final_score, 1),
            'decision': decision,
            'label': self._get_label(final_score, decision),
            'color': color,
            'breakdown': {
                'macro': float(scores['macro']),
                'trend': float(scores['trend']),
                'schedule': float(scores['schedule'])
            },
            'reasons': reasons,
            'factors': self._convert_reasons_to_factors(reasons),
            'action': action,
            'confidence': 'low',
            'category': category,
            'data_available': False
        }
    
    def get_timing_details(self, car_model: str, brand: str = "") -> Dict:
        """
        타이밍 분석 상세 정보
        
        Args:
            car_model: 차량 모델명
            brand: 브랜드명 (옵션)
            
        Returns:
            dict: 상세 분석 결과
        """
        result = self.analyze_timing(car_model, brand)
        
        # 추가 정보
        result['interpretation'] = self._interpret_timing(result['timing_score'])
        
        return result
    
    def _interpret_timing(self, score: float) -> str:
        """
        타이밍 점수 해석
        
        Args:
            score: 타이밍 점수
            
        Returns:
            해석 메시지
        """
        if score >= 80:
            return "매우 좋은 구매 시기입니다. 적극적으로 구매를 고려하세요."
        elif score >= 70:
            return "좋은 구매 시기입니다. 마음에 드는 매물이 있다면 구매하세요."
        elif score >= 60:
            return "보통 수준입니다. 급하지 않다면 조금 더 지켜보는 것도 좋습니다."
        elif score >= 50:
            return "구매 시기로 적합하지 않습니다. 1-2주 후 재평가를 권장합니다."
        else:
            return "구매를 미루는 것이 좋습니다. 1-2개월 후 재평가를 권장합니다."
