"""
Groq AI 서비스
LLM 기반 스마트 분석 (매수/관망 신호, 허위매물 탐지, 네고 대본)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# .env 파일 로드 (ml-service/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# src 폴더를 import path에 추가
src_path = Path(__file__).parent.parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from groq_advisor import GroqCarAdvisor
except ImportError as e:
    print(f"[WARN] Groq module import failed: {e}")
    GroqCarAdvisor = None


class GroqService:
    """Groq AI 서비스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Groq API 키 (선택)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.advisor = None
        
        if GroqCarAdvisor and self.api_key:
            try:
                self.advisor = GroqCarAdvisor(api_key=self.api_key)
            except Exception as e:
                print(f"[WARN] Groq Advisor init failed: {e}")
    
    def is_available(self) -> bool:
        """Groq 서비스 사용 가능 여부"""
        return self.advisor is not None
    
    def generate_signal_report(self, vehicle_data: Dict, prediction_data: Dict, 
                              timing_data: Dict) -> Dict:
        """
        매수/관망 신호등 생성
        
        Args:
            vehicle_data: 차량 정보
            prediction_data: 가격 예측 결과
            timing_data: 타이밍 분석 결과
            
        Returns:
            dict: 신호 분석 결과
        """
        if not self.is_available():
            return self._fallback_signal_report(vehicle_data, prediction_data, timing_data)
        
        try:
            result = self.advisor.generate_signal_report(
                vehicle_data=vehicle_data,
                prediction_data=prediction_data,
                timing_data=timing_data
            )
            return result
        except Exception as e:
            print(f"[WARN] Groq signal analysis failed: {e}")
            return self._fallback_signal_report(vehicle_data, prediction_data, timing_data)
    
    def detect_fraud(self, dealer_description: str, 
                    performance_record: Optional[Dict] = None) -> Dict:
        """
        허위 매물 탐지
        
        Args:
            dealer_description: 딜러 설명글
            performance_record: 성능기록부
            
        Returns:
            dict: 허위 매물 탐지 결과
        """
        if not self.is_available():
            return self._fallback_fraud_detection(dealer_description)
        
        try:
            if performance_record is None:
                performance_record = {
                    'accidents': '알 수 없음',
                    'repairs': '알 수 없음',
                    'replacements': '알 수 없음'
                }
            
            result = self.advisor.detect_fraud(
                dealer_description=dealer_description,
                performance_record=performance_record
            )
            return result
        except Exception as e:
            print(f"[WARN] Groq 허위매물 탐지 실패: {e}")
            return self._fallback_fraud_detection(dealer_description)
    
    def generate_negotiation_script(self, vehicle_data: Dict, prediction_data: Dict,
                                   issues: List[str] = None, 
                                   style: str = 'balanced') -> Dict:
        """
        네고 대본 생성
        
        Args:
            vehicle_data: 차량 정보
            prediction_data: 가격 예측 결과
            issues: 발견된 문제점
            style: 협상 스타일 (aggressive/balanced/friendly)
            
        Returns:
            dict: 네고 대본
        """
        if not self.is_available():
            return self._fallback_negotiation_script(vehicle_data, prediction_data, issues)
        
        try:
            if issues is None:
                issues = []
            
            result = self.advisor.generate_negotiation_script(
                vehicle_data=vehicle_data,
                prediction_data=prediction_data,
                issues=issues,
                style=style
            )
            return result
        except Exception as e:
            print(f"[WARN] Groq 네고 대본 생성 실패: {e}")
            return self._fallback_negotiation_script(vehicle_data, prediction_data, issues)
    
    # ========== Fallback 메서드들 ==========
    
    def _fallback_signal_report(self, vehicle_data: Dict, prediction_data: Dict,
                               timing_data: Dict) -> Dict:
        """Fallback 신호 분석"""
        sale_price = vehicle_data.get('sale_price', 0)
        predicted_price = prediction_data.get('predicted_price', 0)
        timing_score = timing_data.get('timing_score', 50)
        
        if sale_price == 0:
            signal = 'hold'
            message = "판매가 정보가 없어 정확한 분석이 어렵습니다"
        else:
            price_diff_pct = ((sale_price - predicted_price) / predicted_price * 100) if predicted_price > 0 else 0
            
            if price_diff_pct <= -5 and timing_score >= 65:
                signal = 'buy'
                message = "저평가된 매물이며 구매 타이밍도 좋습니다"
            elif price_diff_pct >= 5 or timing_score < 55:
                signal = 'avoid'
                message = "고평가되었거나 구매 타이밍이 좋지 않습니다"
            else:
                signal = 'hold'
                message = "시장 상황을 조금 더 지켜보시기 바랍니다"
        
        signal_map = {
            'buy': {'text': '매수', 'color': '[OK]', 'emoji': '[OK]'},
            'hold': {'text': '관망', 'color': '[?]', 'emoji': '[WARN]'},
            'avoid': {'text': '회피', 'color': '[!]', 'emoji': '[ERROR]'}
        }
        
        info = signal_map[signal]
        
        return {
            'signal': signal,
            'signal_text': info['text'],
            'color': info['color'],
            'emoji': info['emoji'],
            'confidence': 70,
            'short_summary': message,
            'key_points': [
                f"예측가: {predicted_price:,.0f}만원",
                f"타이밍 점수: {timing_score:.1f}점",
                "Groq AI를 사용하면 더 정확한 분석을 받을 수 있습니다"
            ],
            'report': f"{message}. 예측가는 {predicted_price:,.0f}만원이며, 타이밍 점수는 {timing_score:.1f}점입니다."
        }
    
    def _fallback_fraud_detection(self, dealer_description: str) -> Dict:
        """Fallback 허위매물 탐지"""
        suspicious_keywords = ['미세', '단순', '살짝', '조금', '완벽', '최상', '새차급', '무사고']
        warnings = []
        highlighted = []
        
        for keyword in suspicious_keywords:
            if keyword in dealer_description:
                warnings.append(f"[WARN] '{keyword}' 표현 발견 - 주의 필요")
                sentences = dealer_description.split('.')
                for sent in sentences:
                    if keyword in sent and sent.strip():
                        highlighted.append(sent.strip())
        
        return {
            'is_suspicious': len(warnings) > 2,
            'fraud_score': min(len(warnings) * 20, 100),
            'warnings': warnings[:5] if warnings else ["특이사항 없음"],
            'highlighted_text': highlighted[:5],
            'summary': f"{len(warnings)}개의 주의가 필요한 표현이 발견되었습니다." if warnings else "특이사항 없음"
        }
    
    def _fallback_negotiation_script(self, vehicle_data: Dict, prediction_data: Dict,
                                    issues: List[str] = None) -> Dict:
        """Fallback 네고 대본 (고도화 - 체크포인트 반영)"""
        import random
        import time
        
        # 랜덤 시드 (매번 다른 결과)
        random.seed(int(time.time() * 1000) % 2**32)
        
        sale_price = vehicle_data.get('sale_price', 0)
        predicted_price = prediction_data.get('predicted_price', 0)
        brand = vehicle_data.get('brand', '')
        model = vehicle_data.get('model', '차량')
        year = vehicle_data.get('year', '')
        mileage = vehicle_data.get('mileage', 0)
        
        if issues is None:
            issues = []
        
        # 가격 차이 분석
        price_diff = predicted_price - sale_price
        price_diff_pct = (price_diff / predicted_price * 100) if predicted_price > 0 else 0
        
        # 상황별 목표 가격 결정
        if price_diff_pct >= 10:
            situation = "very_cheap"
            target_price = sale_price
        elif price_diff_pct >= 3:
            situation = "cheap"
            target_price = int(sale_price * 0.97)
        elif price_diff_pct >= -3:
            situation = "fair"
            target_price = int(predicted_price * 0.98)
        elif price_diff_pct >= -10:
            situation = "expensive"
            target_price = int(predicted_price)
        else:
            situation = "very_expensive"
            target_price = int(predicted_price * 0.95)
        
        discount = sale_price - target_price
        car_info = f"{brand} {model}" if brand else model
        if year:
            car_info += f" {year}년식"
        
        # 체크포인트 기반 협상 포인트 추가
        issue_mentions = []
        if "타이어 마모 상태" in issues:
            issue_mentions.append(random.choice([
                "타이어 상태도 확인해봐야 할 것 같고요",
                "타이어 교체 비용도 고려해야 할 것 같아서요",
                "타이어 마모 상태가 좀 걱정되네요"
            ]))
        if "동급 매물 대비 높은 가격" in issues:
            issue_mentions.append(random.choice([
                "다른 매물들과 비교했을 때 조금 높은 편이더라구요",
                "비슷한 조건 매물들 시세 확인해봤는데요",
                "주변 시세 대비 좀 높게 책정되신 것 같아요"
            ]))
        if "쿨거래 의사" in issues:
            issue_mentions.append(random.choice([
                "빠르게 결정하고 싶어서요",
                "오늘 바로 계약 가능합니다",
                "현금으로 바로 결제할 수 있어요"
            ]))
        
        # 다양한 문자 대본 템플릿
        msg_templates = {
            "very_cheap": [
                f"안녕하세요, {car_info} 매물 보고 연락드립니다. 가격 좋게 올려주셨네요. {target_price:,}만원에 정리 가능하실까요?",
                f"안녕하세요! {car_info} 관심있어서 연락드려요. 좋은 가격이네요. {target_price:,}만원에 바로 계약할게요!",
                f"{car_info} 매물 봤습니다. 가격 괜찮네요. {target_price:,}만원 가능하시면 오늘 보러갈게요."
            ],
            "cheap": [
                f"안녕하세요, {car_info} 매물 관심있어서 연락드립니다. {target_price:,}만원까지 가능하시면 바로 계약하겠습니다.",
                f"{car_info} 보고 연락드려요. 가격 괜찮은데 {target_price:,}만원에 맞춰주시면 즉시 결정할게요.",
                f"안녕하세요! {car_info} 매물 문의드립니다. {target_price:,}만원 정도면 바로 구매하고 싶습니다."
            ],
            "fair": [
                f"안녕하세요, {car_info} 매물 보고 연락드립니다. 시세가 {predicted_price:,.0f}만원대라서요. {target_price:,}만원에 가능하실까요?",
                f"{car_info} 매물 관심있습니다. 비슷한 매물들 {predicted_price:,.0f}만원대더라구요. {target_price:,}만원 어떠세요?",
                f"안녕하세요! {car_info} 문의드려요. 시세 확인해보니 {predicted_price:,.0f}만원 선이네요. {target_price:,}만원 가능하실까요?"
            ],
            "expensive": [
                f"안녕하세요, {car_info} 매물 관심있는데요. 시세가 {predicted_price:,.0f}만원대라서 {target_price:,}만원 정도로 조정 가능하시면 연락주세요.",
                f"{car_info} 보고 연락드립니다. 다른 매물들이 {predicted_price:,.0f}만원대라 {target_price:,}만원 제안드려요.",
                f"안녕하세요! {car_info} 마음에 드는데 시세 대비 좀 높네요. {target_price:,}만원이면 바로 결정하겠습니다."
            ],
            "very_expensive": [
                f"안녕하세요, {car_info} 매물 관심있습니다. 시세 확인해보니 {predicted_price:,.0f}만원대더라구요. {target_price:,}만원 정도로 조정 가능하실까요?",
                f"{car_info} 문의드립니다. 시세가 {predicted_price:,.0f}만원 선인데 {target_price:,}만원 제안드려요.",
                f"안녕하세요! {car_info} 관심있어요. 시세 대비 높은 편이라 {target_price:,}만원 어떠세요?"
            ]
        }
        
        # 랜덤 선택
        msg = random.choice(msg_templates.get(situation, msg_templates["fair"]))
        
        # 체크포인트가 있으면 메시지에 추가
        if issue_mentions:
            msg += " " + random.choice(issue_mentions)
        
        # 다양한 전화 대본 템플릿
        phone_templates = [
            [
                f"안녕하세요, {car_info} 매물 보고 연락드렸습니다.",
                f"시세 확인해봤는데 {predicted_price:,.0f}만원대더라구요." if issue_mentions else "가격 협의하고 싶어서요.",
                f"{target_price:,}만원에 가능하시면 바로 보러가겠습니다."
            ],
            [
                f"안녕하세요! 올려주신 {car_info} 문의드립니다.",
                random.choice(issue_mentions) if issue_mentions else f"비슷한 매물들 비교해봤는데요.",
                f"{target_price:,}만원 정도면 오늘 바로 결정할 수 있어요."
            ],
            [
                f"안녕하세요, {car_info} 관심있어서 전화드렸습니다.",
                f"다른 매물들 시세가 {predicted_price:,.0f}만원 선이더라구요." if predicted_price > 0 else "가격 조정 가능하신가요?",
                f"{target_price:,}만원에 맞춰주시면 바로 계약하겠습니다."
            ]
        ]
        
        phone = random.choice(phone_templates)
        
        # 협상 팁
        tips_list = [
            "실제로 차량을 꼼꼼히 확인하세요",
            "성능기록부를 반드시 확인하세요",
            "타이어, 브레이크 패드 상태를 점검하세요",
            "빠른 결정 의사를 표현하면 유리합니다",
            "현금 구매시 추가 할인을 요청해보세요",
            "정비 내역을 확인하세요",
            "시세 자료를 미리 준비해가세요"
        ]
        
        return {
            'target_price': target_price,
            'discount_amount': discount,
            'price_situation': situation,
            'message_script': msg,
            'phone_script': phone,
            'tip': random.choice(tips_list),
            'key_arguments': [
                f"시세: {predicted_price:,.0f}만원",
                f"목표가: {target_price:,}만원",
                "즉시 계약 가능"
            ] + issue_mentions[:2],
            'tips': random.sample(tips_list, min(3, len(tips_list))),
            'checkpoints': issues
        }

