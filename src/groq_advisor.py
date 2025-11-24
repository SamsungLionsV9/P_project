"""
Groq LLM 기반 AI 어드바이저
- 매수/관망 신호등 및 근거 리포트
- 허위 매물 탐지
- 네고 대본 생성
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqCarAdvisor:
    """Groq LLM 기반 중고차 AI 어드바이저"""
    
    def __init__(self, api_key=None):
        """
        Args:
            api_key: Groq API 키
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY가 설정되지 않았습니다")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-70b-versatile"  # 가장 똑똑한 모델
    
    def generate_signal_report(self, vehicle_data, prediction_data, timing_data):
        """
        1. 매수/관망 신호등 + 근거 리포트 생성
        
        Args:
            vehicle_data: 차량 정보 (제조사, 모델, 연식, 주행거리, 판매가)
            prediction_data: 가격 예측 결과 (예측가, 신뢰도)
            timing_data: 타이밍 분석 결과 (타이밍 점수, 세부 요소)
            
        Returns:
            dict: {
                'signal': 'buy' | 'hold' | 'avoid',
                'signal_text': '매수' | '관망' | '회피',
                'color': 'green' | 'yellow' | 'red',
                'confidence': 0-100,
                'report': str (상세 근거),
                'short_summary': str (한 줄 요약),
                'key_points': list (핵심 포인트 3-5개)
            }
        """
        # 데이터 준비
        sale_price = vehicle_data.get('sale_price', 0)
        predicted_price = prediction_data.get('predicted_price', 0)
        price_diff = sale_price - predicted_price
        price_diff_pct = (price_diff / predicted_price * 100) if predicted_price > 0 else 0
        
        timing_score = timing_data.get('final_score', 50)
        timing_decision = timing_data.get('decision', '관망')
        
        # 프롬프트 구성
        prompt = f"""당신은 중고차 구매 전문 자문가입니다. 다음 데이터를 분석하여 구매 신호를 판단해주세요.

📊 **차량 정보**
- 차량: {vehicle_data.get('brand')} {vehicle_data.get('model')} {vehicle_data.get('year')}년
- 주행거리: {vehicle_data.get('mileage'):,}km
- 연료: {vehicle_data.get('fuel')}
- 판매가: {sale_price:,}만원

💰 **AI 가격 분석**
- AI 예측가: {predicted_price:,.0f}만원
- 가격 차이: {price_diff:+,.0f}만원 ({price_diff_pct:+.1f}%)
- {'고평가' if price_diff > 0 else '저평가' if price_diff < 0 else '적정가'}

📈 **시장 타이밍 분석**
- 타이밍 점수: {timing_score:.1f}점/100점
- 판단: {timing_decision}
- 거시경제: 금리 {timing_data.get('macro', {}).get('interest_rate', 'N/A')}%, 유가 ${timing_data.get('macro', {}).get('oil_price', 'N/A')}
- 검색 트렌드: {timing_data.get('trend', {}).get('trend_change', 'N/A')}% 변화
- 신차 일정: {len(timing_data.get('schedule', {}).get('upcoming_releases', []))}개 예정

다음 형식으로 JSON을 반환해주세요:
{{
  "signal": "buy" 또는 "hold" 또는 "avoid",
  "confidence": 0-100 숫자,
  "short_summary": "30자 이내 한 줄 요약",
  "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
  "detailed_report": "상세 분석 리포트 (200-300자)"
}}

**판단 기준**:
- buy(매수): 예측가 대비 -5% 이하 + 타이밍 점수 65점 이상
- hold(관망): 예측가 ±5% 이내 또는 타이밍 점수 55-65점
- avoid(회피): 예측가 대비 +5% 이상 또는 타이밍 점수 55점 이하

**리포트 작성 요령**:
1. 가격 평가를 먼저 언급 (고평가/저평가/적정)
2. 시장 상황 설명 (금리, 유가, 검색 트렌드)
3. 신차 출시 일정 영향
4. 종합 판단 및 액션 플랜

JSON만 출력하세요."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 파싱
            # ```json ``` 제거
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            # 신호등 색상 매핑
            signal_map = {
                'buy': {'text': '매수', 'color': '🟢', 'emoji': '✅'},
                'hold': {'text': '관망', 'color': '🟡', 'emoji': '⚠️'},
                'avoid': {'text': '회피', 'color': '🔴', 'emoji': '❌'}
            }
            
            signal_info = signal_map.get(result['signal'], signal_map['hold'])
            
            return {
                'signal': result['signal'],
                'signal_text': signal_info['text'],
                'color': signal_info['color'],
                'emoji': signal_info['emoji'],
                'confidence': result['confidence'],
                'short_summary': result['short_summary'],
                'key_points': result['key_points'],
                'report': result['detailed_report']
            }
            
        except Exception as e:
            print(f"⚠️ Groq API 호출 실패: {e}")
            # Fallback: 규칙 기반
            if price_diff_pct <= -5 and timing_score >= 65:
                signal = 'buy'
            elif price_diff_pct >= 5 or timing_score < 55:
                signal = 'avoid'
            else:
                signal = 'hold'
            
            signal_map = {
                'buy': {'text': '매수', 'color': '🟢', 'emoji': '✅'},
                'hold': {'text': '관망', 'color': '🟡', 'emoji': '⚠️'},
                'avoid': {'text': '회피', 'color': '🔴', 'emoji': '❌'}
            }
            
            signal_info = signal_map[signal]
            
            return {
                'signal': signal,
                'signal_text': signal_info['text'],
                'color': signal_info['color'],
                'emoji': signal_info['emoji'],
                'confidence': 70,
                'short_summary': 'AI 분석 결과를 확인하세요',
                'key_points': [
                    f"예측가 대비 {price_diff_pct:+.1f}%",
                    f"타이밍 점수 {timing_score:.1f}점",
                    "상세 분석은 아래 참고"
                ],
                'report': f"판매가 {sale_price:,}만원, AI 예측가 {predicted_price:,.0f}만원으로 {price_diff_pct:+.1f}% 차이입니다. 타이밍 점수는 {timing_score:.1f}점입니다."
            }
    
    def detect_fraud(self, dealer_description, performance_record):
        """
        2. 허위 매물 & 말장난 탐지
        
        Args:
            dealer_description: 딜러의 설명글 (str)
            performance_record: 성능기록부 데이터 (dict)
                - accidents: 사고 이력
                - repairs: 수리 이력
                - replacements: 교체 부품
                
        Returns:
            dict: {
                'is_suspicious': bool,
                'warnings': list (경고 메시지),
                'highlighted_text': list (형광펜 칠할 문장),
                'fraud_score': 0-100 (의심 점수),
                'summary': str
            }
        """
        prompt = f"""당신은 중고차 매물 검증 전문가입니다. 딜러의 설명글과 성능기록부를 대조하여 허위/과장 광고를 탐지하세요.

📄 **딜러 설명글**:
{dealer_description}

📋 **성능기록부 (실제 기록)**:
- 사고 이력: {performance_record.get('accidents', '없음')}
- 주요 수리: {performance_record.get('repairs', '없음')}
- 교체 부품: {performance_record.get('replacements', '없음')}

다음 형식으로 JSON을 반환하세요:
{{
  "is_suspicious": true 또는 false,
  "fraud_score": 0-100,
  "warnings": ["경고 메시지 1", "경고 메시지 2"],
  "highlighted_sentences": ["의심스러운 문장 1", "의심스러운 문장 2"],
  "summary": "종합 의견 (100자 이내)"
}}

**탐지 기준**:
1. 성능기록부와 모순되는 표현 (예: 사고 이력 있는데 "무사고"라고 표기)
2. 애매모호한 표현 ("미세", "단순", "조금", "살짝")
3. 중요 정보 누락 (수리 이력을 숨김)
4. 과장 광고 ("완벽", "최상", "새차급")

JSON만 출력하세요."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 파싱
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            return {
                'is_suspicious': result['is_suspicious'],
                'fraud_score': result['fraud_score'],
                'warnings': result['warnings'],
                'highlighted_text': result['highlighted_sentences'],
                'summary': result['summary']
            }
            
        except Exception as e:
            print(f"⚠️ Groq API 호출 실패: {e}")
            
            # Fallback: 간단한 키워드 탐지
            suspicious_keywords = ['미세', '단순', '살짝', '조금', '완벽', '최상', '새차급', '무사고']
            warnings = []
            highlighted = []
            
            for keyword in suspicious_keywords:
                if keyword in dealer_description:
                    warnings.append(f"⚠️ '{keyword}' 표현 사용 - 주의 필요")
                    # 문장 찾기
                    sentences = dealer_description.split('.')
                    for sent in sentences:
                        if keyword in sent:
                            highlighted.append(sent.strip())
            
            return {
                'is_suspicious': len(warnings) > 2,
                'fraud_score': min(len(warnings) * 20, 100),
                'warnings': warnings[:5],
                'highlighted_text': highlighted[:5],
                'summary': f"{len(warnings)}개의 의심스러운 표현이 발견되었습니다." if warnings else "특이사항 없음"
            }
    
    def generate_negotiation_script(self, vehicle_data, prediction_data, issues, style='balanced'):
        """
        3. 네고 대본 생성
        
        Args:
            vehicle_data: 차량 정보 (판매가 등)
            prediction_data: AI 예측 결과
            issues: 발견된 문제점 리스트 (타이어 교체 필요, 사고 이력 등)
            style: 'aggressive' | 'balanced' | 'friendly'
            
        Returns:
            dict: {
                'target_price': int (목표 가격),
                'message_script': str (문자 메시지 초안),
                'phone_script': str (전화 대본),
                'key_arguments': list (핵심 논거),
                'tips': list (네고 팁)
            }
        """
        sale_price = vehicle_data.get('sale_price', 0)
        predicted_price = prediction_data.get('predicted_price', 0)
        
        # 목표 가격 계산 (예측가 기준으로 조정)
        target_price = int(predicted_price * 0.98)  # 예측가 -2%
        discount = sale_price - target_price
        
        style_desc = {
            'aggressive': '단호하고 직설적인',
            'balanced': '정중하지만 논리적인',
            'friendly': '부드럽고 우호적인'
        }
        
        prompt = f"""당신은 중고차 가격 협상 전문가입니다. 다음 상황에서 효과적인 네고 대본을 작성하세요.

📊 **상황**:
- 차량: {vehicle_data.get('brand')} {vehicle_data.get('model')}
- 판매가: {sale_price:,}만원
- AI 분석 예측가: {predicted_price:,.0f}만원
- 목표 가격: {target_price:,}만원 (할인액: {discount:,}만원)

⚠️ **발견된 문제점**:
{chr(10).join(f"- {issue}" for issue in issues) if issues else "- 특이사항 없음"}

🎯 **협상 스타일**: {style_desc.get(style, '정중하지만 논리적인')}

다음 형식으로 JSON을 반환하세요:
{{
  "target_price": {target_price},
  "message_script": "문자 메시지 초안 (200자 이내)",
  "phone_script": "전화 통화 대본 (300자 이내)",
  "key_arguments": ["핵심 논거 1", "핵심 논거 2", "핵심 논거 3"],
  "negotiation_tips": ["협상 팁 1", "협상 팁 2", "협상 팁 3"]
}}

**작성 요령**:
1. "빅데이터 분석 결과"를 언급하여 전문성 어필
2. 구체적인 숫자와 근거 제시
3. 문제점을 부드럽게 지적
4. 성실한 구매 의사 표현
5. {style_desc.get(style)} 톤 유지

JSON만 출력하세요."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 파싱
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            return {
                'target_price': result['target_price'],
                'discount_amount': discount,
                'message_script': result['message_script'],
                'phone_script': result['phone_script'],
                'key_arguments': result['key_arguments'],
                'tips': result['negotiation_tips']
            }
            
        except Exception as e:
            print(f"⚠️ Groq API 호출 실패: {e}")
            
            # Fallback: 간단한 템플릿
            return {
                'target_price': target_price,
                'discount_amount': discount,
                'message_script': f"안녕하세요. {vehicle_data.get('model')} 매물 관심있어서 연락드립니다. 빅데이터 분석 결과 적정가가 {target_price:,}만원으로 나왔는데, {target_price:,}만원에 거래 가능할까요?",
                'phone_script': f"제가 여러 매물을 비교 분석해봤는데요, 이 차량의 적정 시세가 {target_price:,}만원 정도더라구요. {target_price:,}만원에 거래 가능하시면 바로 계약하고 싶습니다.",
                'key_arguments': [
                    f"빅데이터 분석 시세: {predicted_price:,.0f}만원",
                    f"요청 할인액: {discount:,}만원",
                    "즉시 계약 가능"
                ],
                'tips': [
                    "성실한 구매 의사 어필",
                    "경쟁 매물 언급",
                    "빠른 결정 제시"
                ]
            }


if __name__ == "__main__":
    # 테스트
    print("=" * 80)
    print("Groq AI 어드바이저 테스트")
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
        
        # 1. 신호등 리포트
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
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("GROQ_API_KEY 환경변수를 설정해주세요")
