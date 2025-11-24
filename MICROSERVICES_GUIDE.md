# 🏗️ 마이크로서비스 아키텍처 가이드

이 프로젝트는 **2개의 독립적인 마이크로서비스**로 구성되어 있습니다.

---

## 📊 서비스 구성

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React/Vue)                  │
│                   프론트엔드 애플리케이션                   │
└────────────────┬────────────────────────┬────────────────┘
                 │                        │
                 ↓                        ↓
    ┌────────────────────┐    ┌────────────────────┐
    │  User Service      │    │   ML Service       │
    │  (Spring Boot)     │    │   (FastAPI)        │
    │  포트: 8080        │    │   포트: 8000       │
    └────────┬───────────┘    └─────────┬──────────┘
             │                           │
             ↓                           ↓
    ┌────────────────┐         ┌─────────────────┐
    │  MySQL DB      │         │  ML Model (.pkl)│
    │  car_database  │         │  + API 데이터    │
    └────────────────┘         └─────────────────┘
```

---

## 🔵 User Service (포트 8080)

### 역할
**사용자 인증 및 회원 관리 전담**

### 기술 스택
- Spring Boot 3.2.0
- Spring Security + JWT
- MySQL 8.0
- Gradle

### API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|-----------|--------|------|----------|
| `/api/auth/health` | GET | 헬스체크 | ❌ |
| `/api/auth/signup` | POST | 회원가입 | ❌ |
| `/api/auth/login` | POST | 로그인 | ❌ |
| `/api/auth/logout` | POST | 로그아웃 | ❌ |
| `/api/auth/me` | GET | 내 정보 조회 | ✅ |
| `/api/auth/update` | PUT | 정보 수정 | ✅ |
| `/api/auth/delete` | DELETE | 회원 탈퇴 | ✅ |

### 데이터베이스
- **테이블**: `users`
- **컬럼**: id, username, email, password, phone_number, role, is_active, created_at, updated_at

### 실행 방법
```bash
cd user-service

# MySQL 설정
mysql -u root -p < setup_mysql.sql

# 설정 파일 생성
cd src/main/resources
cp application.yml.example application.yml
# application.yml에 MySQL 비밀번호 입력

# 실행
cd ../../..
./gradlew bootRun
```

### 테스트
```bash
# 헬스체크
curl http://localhost:8080/api/auth/health

# 회원가입
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "phoneNumber": "010-1234-5678"
  }'
```

---

## 🟢 ML Service (포트 8000)

### 역할
**차량 가격 예측 및 구매 타이밍 분석 전담**

### 기술 스택
- FastAPI
- XGBoost (ML 모델)
- Groq AI (LLM)
- Python 3.8+

### API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|-----------|--------|------|----------|
| `/api/health` | GET | 헬스체크 | ❌ |
| `/api/predict` | POST | 가격 예측 | ❌ |
| `/api/timing` | POST | 타이밍 분석 | ❌ |
| `/api/smart-analysis` | POST | 통합 스마트 분석 | ❌ |
| `/api/brands` | GET | 브랜드 목록 | ❌ |
| `/api/models/{brand}` | GET | 브랜드별 모델 목록 | ❌ |
| `/api/fuel-types` | GET | 연료 타입 목록 | ❌ |

### 데이터 소스
- **ML 모델**: `improved_car_price_model.pkl`
- **학습 데이터**: 119,343대의 중고차 데이터
- **실시간 데이터**: 한국은행 API, 네이버 데이터랩 API
- **Groq AI**: 선택적 기능 (API 키 필요)

### 실행 방법
```bash
cd ml-service

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (선택)
cp .env.example .env  # (만약 있다면)
# .env에 GROQ_API_KEY 입력

# 실행
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API 문서
브라우저에서 자동 생성된 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 테스트
```bash
# 헬스체크
curl http://localhost:8000/api/health

# 브랜드 목록
curl http://localhost:8000/api/brands

# 현대 브랜드의 모델 목록
curl http://localhost:8000/api/models/현대

# 연료 타입 목록
curl http://localhost:8000/api/fuel-types

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

# 통합 스마트 분석
curl -X POST "http://localhost:8000/api/smart-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린",
    "sale_price": 3200,
    "dealer_description": "완벽한 차량입니다."
  }'
```

---

## 🔗 서비스 간 통신

### 현재 구조: 독립 실행
- 각 서비스는 **독립적으로 실행**됩니다
- 프론트엔드가 두 서비스에 **직접 API 호출**
- 서비스 간 직접 통신 없음

### 통신 예시 (프론트엔드)
```javascript
// 1. User Service에서 로그인
const loginResponse = await fetch('http://localhost:8080/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { token } = await loginResponse.json();

// 2. ML Service에서 가격 예측 (인증 불필요)
const predictResponse = await fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    brand: '현대',
    model: '그랜저',
    year: 2022,
    mileage: 35000,
    fuel: '가솔린'
  })
});
const prediction = await predictResponse.json();
```

---

## 🚀 동시 실행 방법

### 터미널 1: User Service
```bash
cd user-service
./gradlew bootRun
# 포트 8080에서 실행 중...
```

### 터미널 2: ML Service
```bash
cd ml-service
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 포트 8000에서 실행 중...
```

### 확인
```bash
# User Service
curl http://localhost:8080/api/auth/health

# ML Service
curl http://localhost:8000/api/health
```

---

## 📋 왜 이렇게 분리했나요?

### ✅ 장점

1. **기술 스택 자유도**
   - User Service: Spring Boot (엔터프라이즈급 인증)
   - ML Service: FastAPI (ML/AI에 최적화)

2. **독립적인 확장**
   - 예측 요청이 많으면 ML Service만 스케일 아웃
   - 회원가입이 많으면 User Service만 스케일 아웃

3. **독립적인 배포**
   - ML 모델 업데이트 시 User Service 무중단
   - 인증 로직 변경 시 ML Service 무영향

4. **팀별 개발**
   - 백엔드 팀: User Service
   - ML 팀: ML Service
   - 독립적으로 개발 및 테스트

5. **장애 격리**
   - ML Service 장애 시에도 로그인/회원가입 가능
   - User Service 장애 시에도 예측 API 사용 가능 (공개 API)

---

## 🔐 보안 고려사항

### ML Service의 공개 API
현재 ML Service의 모든 엔드포인트는 **인증 없이** 접근 가능합니다.

**이유:**
- 빠른 프로토타입 개발
- 데모 및 테스트 용이성
- 민감한 데이터 미포함

**프로덕션 환경 권장사항:**
```python
# ML Service에 JWT 검증 추가 (선택사항)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # User Service에서 발급한 JWT 검증
    token = credentials.credentials
    # JWT 검증 로직...
    return user_id

@app.post("/api/predict")
async def predict(request: PredictRequest, user_id: str = Depends(verify_token)):
    # 인증된 사용자만 접근 가능
    ...
```

---

## 📚 관련 문서

- **User Service 설정**: [user-service/SETUP_GUIDE.md](user-service/SETUP_GUIDE.md)
- **ML Service 가이드**: [ml-service/README.md](ml-service/README.md)
- **API 테스트 결과**: [API_TEST_RESULTS.md](API_TEST_RESULTS.md)
- **프로젝트 아키텍처**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🤔 자주 묻는 질문

### Q: 왜 User Service에 차량 API가 없나요?
**A**: 마이크로서비스 원칙에 따라 각 서비스는 **단일 책임**만 가집니다.
- User Service = 인증/회원 관리만
- ML Service = 차량/예측 관련 모든 것

### Q: 두 서비스가 데이터를 공유하나요?
**A**: 아니요. 각 서비스는 **독립적인 데이터 소스**를 사용합니다.
- User Service → MySQL (users 테이블)
- ML Service → ML 모델 파일 + 외부 API

### Q: 프론트엔드는 어떻게 개발하나요?
**A**: 두 API를 **동시에 호출**하면 됩니다.
```javascript
// 사용자 정보는 8080에서
const user = await fetch('http://localhost:8080/api/auth/me', {
  headers: { Authorization: `Bearer ${token}` }
});

// 가격 예측은 8000에서
const prediction = await fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  body: JSON.stringify(carData)
});
```

---

**마이크로서비스 아키텍처의 핵심은 "분리"입니다!** 🎯

