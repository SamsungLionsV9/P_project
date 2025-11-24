# 🏗️ 시스템 아키텍처 및 Groq API 실행 로직

## 📂 프로젝트 구조

```
used-car-price-predictor/
│
├── 📁 src/                              # 소스 코드
│   │
│   ├── 🤖 AI 어드바이저 (v3.0 - 최신)
│   │   ├── groq_advisor.py              # Groq LLM 핵심 기능
│   │   └── smart_advisor.py             # 통합 스마트 어드바이저
│   │
│   ├── 💎 실제 데이터 기반 (v2.0)
│   │   ├── car_sentix_real.py           # 타이밍 분석
│   │   ├── integrated_advisor_real.py   # 통합 어드바이저
│   │   ├── timing_engine_real.py        # 타이밍 점수 계산
│   │   └── data_collectors_real_only.py # 실제 데이터 수집
│   │
│   ├── 💰 가격 예측
│   │   ├── predict_car_price.py         # 가격 예측 (추론)
│   │   └── train_model_improved.py      # 모델 학습
│   │
│   └── 📊 데이터 수집
│       ├── data_collectors_real.py      # 실시간 API
│       └── data_collectors.py           # 신차 일정
│
├── 📁 models/                           # 학습된 모델
│   └── improved_car_price_model.pkl
│
├── 📁 data/                             # 데이터
│   ├── processed_encar_data.csv
│   ├── new_car_schedule.csv
│   └── vehicle_sentiment.json
│
├── 📁 docs/                             # 문서
│   ├── ARCHITECTURE.md                  # 이 문서
│   ├── GROQ_AI_FEATURES.md              # Groq 기능 가이드
│   └── REAL_DATA_USAGE.md               # 실제 데이터 가이드
│
├── .env                                 # API 키 (gitignore)
├── requirements.txt
└── README.md
```

---

## 🔄 Groq API 실행 로직

### 전체 데이터 흐름

```
사용자 입력
    ↓
┌─────────────────────────────────────┐
│  smart_advisor.py (메인 진입점)    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 1: 데이터 수집                │
│  - 가격 예측 (XGBoost)              │
│  - 타이밍 분석 (API 데이터)         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 2: Groq AI 분석               │
│  groq_advisor.py                     │
│  ├─ generate_signal_report()        │
│  ├─ detect_fraud()                  │
│  └─ generate_negotiation_script()   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Step 3: 결과 통합 및 출력          │
│  - 신호등 + 리포트                  │
│  - 허위 매물 경고                    │
│  - 네고 대본                         │
└─────────────────────────────────────┘
```

---

## 🤖 Groq API 상세 로직

### 1. 초기화 및 연결

```python
# groq_advisor.py

from groq import Groq

class GroqCarAdvisor:
    def __init__(self, api_key=None):
        # 1. API 키 로드 (.env 파일에서)
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        # 2. Groq 클라이언트 생성
        self.client = Groq(api_key=self.api_key)
        
        # 3. 모델 지정 (최신 Llama 3.3 70B)
        self.model = "llama-3.3-70b-versatile"
```

**핵심 포인트:**
- `.env` 파일에서 `GROQ_API_KEY` 자동 로드
- 클라이언트 한 번만 초기화
- 최신 모델 사용 (70B 파라미터)

---

### 2. 매수/관망 신호등 생성

```python
def generate_signal_report(vehicle_data, prediction_data, timing_data):
    # Step 1: 데이터 준비
    sale_price = vehicle_data['sale_price']
    predicted_price = prediction_data['predicted_price']
    timing_score = timing_data['final_score']
    
    # Step 2: 프롬프트 구성
    prompt = f"""
    당신은 중고차 구매 전문 자문가입니다.
    
    차량: {vehicle_data}
    AI 예측가: {predicted_price}만원
    판매가: {sale_price}만원
    타이밍 점수: {timing_score}점
    
    다음 JSON 형식으로 판단해주세요:
    {{
      "signal": "buy" | "hold" | "avoid",
      "confidence": 0-100,
      "short_summary": "...",
      "key_points": [...],
      "detailed_report": "..."
    }}
    """
    
    # Step 3: Groq API 호출
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,    # 일관성 있는 응답
        max_tokens=1000
    )
    
    # Step 4: JSON 파싱
    result_text = response.choices[0].message.content
    result = json.loads(result_text)
    
    # Step 5: 신호등 색상 매핑
    signal_map = {
        'buy': {'text': '매수', 'color': '🟢'},
        'hold': {'text': '관망', 'color': '🟡'},
        'avoid': {'text': '회피', 'color': '🔴'}
    }
    
    return {
        'signal': result['signal'],
        'signal_text': signal_map[result['signal']]['text'],
        'color': signal_map[result['signal']]['color'],
        'confidence': result['confidence'],
        'short_summary': result['short_summary'],
        'key_points': result['key_points'],
        'report': result['detailed_report']
    }
```

**실행 흐름:**
1. 데이터 준비 (가격, 타이밍 점수)
2. 프롬프트에 데이터 삽입
3. Groq API 호출 (HTTP POST)
4. JSON 응답 파싱
5. 한글 매핑 및 반환

**Groq API 통신:**
```
Client (Python) 
    ↓ HTTPS
Groq API Server
    ↓ GPU 추론
Llama-3.3-70B 모델
    ↓ 생성
JSON 응답
    ↓
Client (파싱)
```

---

### 3. 허위 매물 탐지

```python
def detect_fraud(dealer_description, performance_record):
    # Step 1: 프롬프트 구성
    prompt = f"""
    딜러 설명글:
    {dealer_description}
    
    성능기록부:
    - 사고: {performance_record['accidents']}
    - 수리: {performance_record['repairs']}
    
    모순, 과장, 애매한 표현을 찾아 JSON으로 반환:
    {{
      "is_suspicious": true/false,
      "fraud_score": 0-100,
      "warnings": [...],
      "highlighted_sentences": [...]
    }}
    """
    
    # Step 2: API 호출
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # 더 엄격한 판단
        max_tokens=800
    )
    
    # Step 3: 결과 반환
    result = json.loads(response.choices[0].message.content)
    return result
```

**핵심 로직:**
- 텍스트 대조 분석 (딜러 vs 성능기록부)
- 의심 키워드 감지 ("미세", "단순", "최상" 등)
- 의심 점수 0-100 계산

---

### 4. 네고 대본 생성

```python
def generate_negotiation_script(vehicle_data, prediction_data, issues, style):
    # Step 1: 목표 가격 계산
    target_price = int(prediction_data['predicted_price'] * 0.98)
    discount = vehicle_data['sale_price'] - target_price
    
    # Step 2: 스타일별 프롬프트
    style_desc = {
        'aggressive': '단호하고 직설적인',
        'balanced': '정중하지만 논리적인',
        'friendly': '부드럽고 우호적인'
    }
    
    prompt = f"""
    협상 대본 작성:
    판매가: {vehicle_data['sale_price']}만원
    목표가: {target_price}만원
    문제점: {issues}
    스타일: {style_desc[style]}
    
    JSON 반환:
    {{
      "message_script": "문자 초안",
      "phone_script": "전화 대본",
      "key_arguments": [...],
      "negotiation_tips": [...]
    }}
    """
    
    # Step 3: API 호출 (창의성 높임)
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,  # 창의적 대본
        max_tokens=1200
    )
    
    return json.loads(response.choices[0].message.content)
```

**특징:**
- 스타일 선택 가능 (공격형/균형형/우호형)
- 빅데이터 근거 자동 삽입
- 실전에서 바로 쓸 수 있는 대본

---

## 🔐 API 키 관리

### .env 파일 구조

```env
# Groq API (필수)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# 한국은행 API (선택)
BOK_API_KEY=EXZHBLWFBSPD12N6J4EP

# 네이버 API (선택)
NAVER_CLIENT_ID=uie8gJc_Yjg_pscE3YTY
NAVER_CLIENT_SECRET=Q8w4fb3J0b
```

### 키 로드 방식

```python
from dotenv import load_dotenv
import os

# .env 파일 자동 로드
load_dotenv()

# 환경변수에서 키 가져오기
groq_key = os.getenv('GROQ_API_KEY')
```

**보안:**
- `.env` 파일은 `.gitignore`에 포함
- GitHub에 절대 커밋 안 됨
- 로컬에만 저장

---

## 📊 데이터 흐름 상세

### 전체 파이프라인

```
┌─────────────────┐
│  사용자 입력    │
│  (차량 정보)    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ data_collectors │  ← 한국은행 API
│ (실시간 데이터) │  ← Yahoo Finance
│                 │  ← 네이버 데이터랩
└────────┬────────┘
         ↓
┌─────────────────┐
│ XGBoost Model   │  ← improved_car_price_model.pkl
│ (가격 예측)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ timing_engine   │
│ (점수 계산)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Groq LLM        │  ← GROQ_API_KEY
│ (AI 해석)       │  → JSON 응답
└────────┬────────┘
         ↓
┌─────────────────┐
│  최종 리포트    │
│  - 신호등       │
│  - 허위 탐지    │
│  - 네고 대본    │
└─────────────────┘
```

---

## ⚡ 성능 최적화

### 1. Groq API 속도
- **평균 응답 시간**: 2-3초
- **이유**: Groq의 LPU(Language Processing Unit) 사용
- **일반 LLM 대비**: 5-10배 빠름

### 2. 캐싱 전략
```python
# 동일 차량은 캐시 사용
cache = {}

def get_analysis(car_model):
    if car_model in cache:
        return cache[car_model]
    
    result = groq_advisor.analyze(car_model)
    cache[car_model] = result
    return result
```

### 3. Fallback 메커니즘
```python
try:
    # Groq API 시도
    result = advisor.generate_signal_report(...)
except Exception as e:
    # 실패 시 규칙 기반으로 Fallback
    result = rule_based_signal(...)
```

---

## 🧪 테스트 방법

### 단위 테스트
```bash
# Groq API만 테스트
cd src
python test_groq_full.py
```

### 통합 테스트
```bash
# 전체 시스템 테스트
python smart_advisor.py 현대 그랜저 2022 35000 가솔린 3200
```

### 결과 확인
```bash
# JSON 파일 생성됨
ls smart_analysis_*.json
```

---

## 📈 확장 가능성

### 1. 다른 LLM 추가
```python
# OpenAI GPT-4 추가
if use_groq:
    advisor = GroqCarAdvisor()
elif use_openai:
    advisor = OpenAIAdvisor()
```

### 2. 실시간 스트리밍
```python
# 응답을 실시간으로 받기
for chunk in client.chat.completions.create(
    model=self.model,
    messages=[...],
    stream=True
):
    print(chunk.choices[0].delta.content)
```

### 3. 멀티모달 (이미지 분석)
```python
# 차량 사진 분석 추가
result = advisor.analyze_vehicle_image(image_url)
```

---

## 🔍 디버깅 팁

### 1. Groq API 오류
```python
try:
    response = self.client.chat.completions.create(...)
except Exception as e:
    print(f"Groq API 오류: {e}")
    # 상세 오류 로그
    import traceback
    traceback.print_exc()
```

### 2. 프롬프트 확인
```python
# 프롬프트 출력
print("=" * 80)
print("📝 Groq에게 전송하는 프롬프트:")
print(prompt)
print("=" * 80)
```

### 3. 응답 검증
```python
# JSON 파싱 전 확인
print(f"Groq 응답: {response.choices[0].message.content}")

# JSON 형식 검증
try:
    result = json.loads(response_text)
except json.JSONDecodeError:
    print("❌ JSON 파싱 실패")
    print(f"응답 내용: {response_text}")
```

---

## 💡 프롬프트 엔지니어링 팁

### 1. 구조화된 출력 요청
```
✅ 좋은 예:
"다음 JSON 형식으로 반환하세요: {"signal": "buy", ...}"

❌ 나쁜 예:
"분석해주세요"
```

### 2. Few-shot 예시 제공
```python
prompt = f"""
예시:
입력: 판매가 3000만원, 예측가 2800만원
출력: {{"signal": "avoid", "reason": "고평가"}}

실제 데이터:
입력: 판매가 {sale_price}, 예측가 {predicted_price}
출력:
"""
```

### 3. 온도(Temperature) 조절
- `0.1-0.3`: 일관성 (신호등, 탐지)
- `0.4-0.7`: 창의성 (네고 대본)
- `0.8-1.0`: 다양성 (브레인스토밍)

---

## 📚 참고 자료

- **Groq 공식 문서**: https://console.groq.com/docs
- **Llama 3.3 모델 가이드**: https://www.llama.com/
- **프롬프트 엔지니어링**: https://www.promptingguide.ai/

---

## 🎯 핵심 요약

1. **Groq API**: 초고속 LLM 추론 (2-3초)
2. **3단계 흐름**: 데이터 수집 → Groq 분석 → 결과 출력
3. **3대 기능**: 신호등 + 허위 탐지 + 네고 대본
4. **Fallback**: API 실패 시 규칙 기반
5. **보안**: `.env`로 API 키 관리

**핵심 철학**: 데이터는 객관적으로, 해석은 AI가 논리적으로!
