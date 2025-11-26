# 중고차 가격 예측 ML 서비스 (FastAPI)

FastAPI 기반 중고차 가격 예측 및 구매 타이밍 분석 API - 머신러닝 마이크로서비스

## 📁 프로젝트 구조

```
ml-service/
├── main.py                   # FastAPI 메인 애플리케이션
├── requirements.txt          # Python 의존성
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic 스키마 정의
├── services/
│   ├── __init__.py
│   ├── prediction.py         # 가격 예측 서비스
│   ├── timing.py             # 타이밍 분석 서비스
│   └── groq_service.py       # Groq AI 서비스
└── utils/
    ├── __init__.py
    ├── model_loader.py       # ML 모델 로더
    └── validators.py         # 입력 검증
```

## 🚀 실행 방법

### 1. 의존성 설치

```bash
cd ml-service
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (선택)

Groq AI 기능을 사용하려면 `.env` 파일을 생성하세요:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 3. 서버 실행

```bash
# 개발 모드 (자동 리로드)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는
python -m ml-service.main
```

### 4. API 문서 확인

브라우저에서 다음 URL을 열어 자동 생성된 API 문서를 확인하세요:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API 엔드포인트

### 헬스체크
- `GET /api/health` - 서버 상태 확인

### 가격 예측
- `POST /api/predict` - 차량 가격 예측

```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린"
}
```

### 타이밍 분석
- `POST /api/timing` - 구매 타이밍 분석

```json
{
  "model": "그랜저"
}
```

### 통합 스마트 분석
- `POST /api/smart-analysis` - 가격 예측 + 타이밍 + Groq AI 통합 분석

```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "sale_price": 3200,
  "dealer_description": "완벽한 차량입니다."
}
```

### 메타데이터
- `GET /api/brands` - 지원하는 브랜드 목록
- `GET /api/models/{brand}` - 브랜드별 모델 목록
- `GET /api/fuel-types` - 연료 타입 목록

## 🔑 주요 기능

### 1️⃣ 가격 예측
- XGBoost 기반 ML 모델
- 119,343대의 실제 중고차 데이터로 학습
- ±10% 가격 범위 제공
- 신뢰도 점수 포함

### 2️⃣ 타이밍 분석
- 거시경제 지표 (금리, 환율, 유가)
- 검색 트렌드 분석
- 신차 출시 일정
- 0-100점 타이밍 점수

### 3️⃣ Groq AI 분석 (선택)
- 매수/관망/회피 신호등
- 허위 매물 탐지
- 네고 대본 자동 생성
- LLM 기반 상세 리포트

## 🧪 테스트

### cURL 예제

```bash
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
```

### Python 예제

```python
import requests

# 가격 예측
response = requests.post('http://localhost:8000/api/predict', json={
    'brand': '현대',
    'model': '그랜저',
    'year': 2022,
    'mileage': 35000,
    'fuel': '가솔린'
})

print(response.json())
```

## ⚙️ 설정

### 모델 파일 위치
가격 예측 모델 파일은 다음 경로 중 하나에 있어야 합니다:
- `improved_car_price_model.pkl`
- `models/improved_car_price_model.pkl`
- `../improved_car_price_model.pkl`

모델이 없으면 `train_model_improved.py`를 실행하여 먼저 학습시키세요.

## 🐛 문제 해결

### 모델을 찾을 수 없습니다
```bash
# 프로젝트 루트에서 모델 학습
python src/train_model_improved.py
```

### Groq AI가 작동하지 않습니다
- `.env` 파일에 `GROQ_API_KEY`가 설정되어 있는지 확인
- Groq API가 없어도 기본 기능은 작동합니다

### Import 오류
```bash
# ml-service 폴더를 패키지로 인식시키기
cd /path/to/used-car-price-predictor-main
python -m ml-service.main
```

## 📄 라이센스

MIT License

