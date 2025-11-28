# 🚗 중고차 가격 예측 API - ML 서비스 구조 완성

## 📁 마이크로서비스 아키텍처

```
used-car-price-predictor-main/
├── ml-service/                       # 🆕 ML & 자동차 분석 서비스 (FastAPI)
│   ├── main.py                       # FastAPI 메인 애플리케이션
│   ├── run.sh                        # 서버 실행 스크립트
│   ├── requirements.txt              # 서비스 의존성
│   ├── README.md                     # 서비스 문서
│   │
│   ├── models/                       # Pydantic 스키마
│   │   ├── __init__.py
│   │   └── schemas.py                # API 요청/응답 모델
│   │
│   ├── services/                     # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── prediction.py             # 가격 예측 서비스
│   │   ├── timing.py                 # 타이밍 분석 서비스
│   │   └── groq_service.py           # Groq AI 서비스
│   │
│   └── utils/                        # 유틸리티
│       ├── __init__.py
│       ├── model_loader.py           # ML 모델 로더
│       └── validators.py             # 입력 검증
│
├── user-service/                     # 🆕 사용자 관리 서비스 (Spring Boot)
│   ├── src/                          # Spring Boot 소스
│   ├── build.gradle                  # Gradle 설정
│   └── ...                           # JWT 인증, MySQL 연동
│
├── src/                              # 기존 소스 코드
│   ├── predict_car_price.py          # 가격 예측 (CLI)
│   ├── integrated_advisor_real.py    # 통합 어드바이저
│   ├── timing_engine_real.py         # 타이밍 엔진
│   ├── groq_advisor.py               # Groq AI 어드바이저
│   └── ...
│
├── data/                             # 데이터
├── docs/                             # 문서
└── requirements.txt                  # 프로젝트 의존성
```

## 🎯 구현된 API 엔드포인트

### 1️⃣ 헬스체크
```
GET  /api/health
```

### 2️⃣ 가격 예측
```
POST /api/predict

Request:
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린"
}

Response:
{
  "predicted_price": 3200,
  "price_range": [2880, 3520],
  "confidence": 0.87
}
```

### 3️⃣ 타이밍 분석
```
POST /api/timing

Request:
{
  "model": "그랜저"
}

Response:
{
  "timing_score": 75.5,
  "decision": "구매 적기",
  "color": "🟢",
  "breakdown": {
    "macro": 78.2,
    "trend": 72.5,
    "schedule": 75.8
  },
  "reasons": [
    "✅ 저금리 2.5% (구매 적기)",
    "✅ 관심도 안정 (5.2%)",
    "✅ 신차 출시 예정 없음"
  ]
}
```

### 4️⃣ 통합 스마트 분석
```
POST /api/smart-analysis

Request:
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "sale_price": 3200,
  "dealer_description": "완벽한 차량입니다. 무사고입니다."
}

Response:
{
  "prediction": {
    "predicted_price": 3200,
    "price_range": [2880, 3520],
    "confidence": 0.87
  },
  "timing": {
    "timing_score": 75.5,
    "decision": "구매 적기",
    "color": "🟢",
    "breakdown": {...},
    "reasons": [...]
  },
  "groq_analysis": {
    "signal": {
      "signal": "buy",
      "signal_text": "매수",
      "color": "🟢",
      "confidence": 85,
      "key_points": [...],
      "report": "..."
    },
    "fraud_check": {
      "is_suspicious": false,
      "fraud_score": 20,
      "warnings": [...],
      "summary": "..."
    },
    "negotiation": {
      "target_price": 3136,
      "discount_amount": 64,
      "message_script": "...",
      "phone_script": "...",
      "key_arguments": [...],
      "tips": [...]
    }
  }
}
```

### 5️⃣ 메타데이터
```
GET  /api/brands              # 브랜드 목록
GET  /api/models/{brand}      # 브랜드별 모델 목록
GET  /api/fuel-types          # 연료 타입 목록
```

## 🚀 실행 방법

### 1. 의존성 설치

```bash
cd ml-service
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (선택)

프로젝트 루트에 `.env` 파일 생성:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 3. 서버 실행

**방법 1: 실행 스크립트 사용**
```bash
cd ml-service
./run.sh
```

**방법 2: 직접 실행**
```bash
# 프로젝트 루트에서
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000 --reload
```

**방법 3: Python 모듈로 실행**
```bash
cd ml-service
python main.py
```

### 4. API 문서 확인

브라우저에서 다음 URL을 열어 자동 생성된 API 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 API 테스트

### cURL 테스트

```bash
# 헬스체크
curl http://localhost:8000/api/health

# 가격 예측
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린"
  }'

# 타이밍 분석
curl -X POST "http://localhost:8000/api/timing" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "그랜저"
  }'

# 통합 분석
curl -X POST "http://localhost:8000/api/smart-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린",
    "sale_price": 3200
  }'
```

### Python 테스트

```python
import requests

# 기본 URL
BASE_URL = "http://localhost:8000"

# 가격 예측
response = requests.post(f"{BASE_URL}/api/predict", json={
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린"
})

print("가격 예측 결과:")
print(response.json())

# 타이밍 분석
response = requests.post(f"{BASE_URL}/api/timing", json={
    "model": "그랜저"
})

print("\n타이밍 분석 결과:")
print(response.json())

# 통합 분석
response = requests.post(f"{BASE_URL}/api/smart-analysis", json={
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린",
    "sale_price": 3200,
    "dealer_description": "완벽한 차량입니다."
})

print("\n통합 분석 결과:")
print(response.json())
```

## 🔑 주요 기능

### ✅ 구현 완료
- ✅ FastAPI 기반 REST API
- ✅ 가격 예측 엔드포인트
- ✅ 타이밍 분석 엔드포인트
- ✅ 통합 스마트 분석 엔드포인트
- ✅ Groq AI 통합 (신호등, 허위매물, 네고)
- ✅ 입력 데이터 검증
- ✅ 메타데이터 API (브랜드, 모델, 연료)
- ✅ CORS 지원
- ✅ 자동 API 문서 생성 (Swagger/ReDoc)
- ✅ 에러 핸들링
- ✅ Pydantic 스키마 검증

### 🎯 핵심 기술
- **FastAPI**: 고성능 웹 프레임워크
- **Pydantic**: 타입 안전 데이터 검증
- **XGBoost**: 가격 예측 ML 모델
- **Groq LLM**: AI 기반 스마트 분석
- **실시간 데이터**: 한국은행, 네이버 데이터랩, Yahoo Finance

## 📊 데이터 흐름

```
사용자 요청
    ↓
FastAPI 엔드포인트 (main.py)
    ↓
입력 검증 (validators.py)
    ↓
서비스 레이어 (services/)
    ├── prediction.py → ML 모델 → 가격 예측
    ├── timing.py → 실시간 데이터 수집 → 타이밍 점수
    └── groq_service.py → Groq LLM → AI 분석
    ↓
Pydantic 응답 모델 (schemas.py)
    ↓
JSON 응답
```

## 🐛 문제 해결

### 1. 모델 파일을 찾을 수 없습니다

```bash
# 프로젝트 루트에서 모델 학습
python src/train_model_improved.py
```

### 2. Import 오류

```bash
# 프로젝트 루트에서 실행
cd /path/to/used-car-price-predictor-main
python -m uvicorn ml-service.main:app --reload
```

### 3. Groq AI가 작동하지 않습니다

- `.env` 파일에 `GROQ_API_KEY` 확인
- Groq API가 없어도 기본 기능은 작동합니다 (Fallback 제공)

### 4. 실시간 데이터 수집 실패

- 네이버 데이터랩 API 키 확인
- 한국은행 API 키 확인
- 타이밍 분석은 Fallback 모드로 작동합니다

## 📝 다음 단계

### 프론트엔드 연동
1. React/Vue.js 프론트엔드 개발
2. API 호출 통합
3. UI/UX 디자인

### 배포
1. Docker 컨테이너화
2. AWS/GCP 배포
3. CI/CD 파이프라인 구축
4. HTTPS 설정

### 추가 기능
1. 사용자 인증/인가
2. 검색 히스토리 저장
3. 차량 비교 기능
4. 알림 기능

## 📄 라이센스

MIT License

---

**구현 완료일**: 2025년 11월 24일  
**아키텍처**: 마이크로서비스 (ML Service + User Service)  
**기술 스택**: 
- ML Service: FastAPI, Python 3.8+, XGBoost, Groq LLM
- User Service: Spring Boot 3.2, MySQL 8.0, JWT, Spring Security  
**API 버전**: 1.0.0

