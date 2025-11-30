"""
타이밍 분석 서비스
거시경제, 검색 트렌드, 신차 일정을 분석하여 구매 타이밍 판단
"""

import sys
import os
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
    
    def __init__(self):
        if RealTimingEngine:
            self.timing_engine = RealTimingEngine()
        else:
            self.timing_engine = None
    
    def analyze_timing(self, car_model: str) -> Dict:
        """
        타이밍 분석
        
        Args:
            car_model: 차량 모델명
            
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
            return self._fallback_timing_analysis(car_model)
        
        try:
            # 실제 데이터 수집
            data = collect_real_data_only(car_model)
            
            # 타이밍 점수 계산
            result = self.timing_engine.calculate_timing_score(
                macro_data=data['macro'],
                trend_data=data['trend'],
                schedule_data=data['schedule'],
                car_model=car_model
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
                'data_available': True
            }
            
        except Exception as e:
            print(f"⚠️ 타이밍 분석 중 오류: {e}")
            return self._fallback_timing_analysis(car_model)
    
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
            
            if '✅' in reason or '🟢' in reason or '좋' in reason or '추천' in reason or '상승' in reason:
                status = 'positive'
            elif '❌' in reason or '🔴' in reason or '주의' in reason or '하락' in reason or '위험' in reason:
                status = 'negative'
            else:
                status = 'neutral'
            
            factors.append({
                'factor': 'timing',
                'status': status,
                'description': clean_reason
            })
        return factors
    
    def _fallback_timing_analysis(self, car_model: str) -> Dict:
        """
        Fallback 타이밍 분석 (데이터 수집 실패 시)
        
        Args:
            car_model: 차량 모델명
            
        Returns:
            dict: 기본 타이밍 분석 결과
        """
        reasons = [
            "⚠️ 실시간 데이터를 불러올 수 없습니다",
            "⚠️ 기본 분석 결과를 제공합니다",
            "⚠️ 자세한 분석을 위해 시스템 관리자에게 문의하세요"
        ]
        
        # 기본값 반환 (앱 호환 필드 포함)
        return {
            'timing_score': 60.0,
            'decision': '관망',
            'label': '보통',
            'color': '🟡',
            'breakdown': {
                'macro': 60.0,
                'trend': 60.0,
                'schedule': 60.0
            },
            'reasons': reasons,
            'factors': self._convert_reasons_to_factors(reasons),
            'action': '시장 상황 지켜보기',
            'confidence': 'low',
            'data_available': False
        }
    
    def get_timing_details(self, car_model: str) -> Dict:
        """
        타이밍 분석 상세 정보
        
        Args:
            car_model: 차량 모델명
            
        Returns:
            dict: 상세 분석 결과
        """
        result = self.analyze_timing(car_model)
        
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

