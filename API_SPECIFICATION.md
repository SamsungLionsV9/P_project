# 🚀 중고차 가격 예측 시스템 - API 명세서 v1.0

**최종 업데이트**: 2025년 11월 24일  
**아키텍처**: 마이크로서비스 (ML Service + User Service)  
**Base URLs**:
- ML Service: `http://localhost:8000`
- User Service: `http://localhost:8080`

---

## 📋 목차

1. [개요](#-개요)
2. [인증](#-인증)
3. [공통 응답 형식](#-공통-응답-형식)
4. [에러 코드](#-에러-코드)
5. [ML Service API](#-ml-service-api-포트-8000)
6. [User Service API](#-user-service-api-포트-8080)
7. [데이터 모델](#-데이터-모델)
8. [통합 시나리오](#-통합-시나리오)
9. [버전 히스토리](#-버전-히스토리)

---

## 🎯 개요

중고차 가격 예측 및 구매 의사결정 지원 시스템의 REST API 명세서입니다.

### 서비스 구성

```
┌─────────────────────────────────────────┐
│         Frontend Application             │
└───────────┬────────────────┬─────────────┘
            │                │
            ↓                ↓
    ┌──────────────┐  ┌──────────────┐
    │ ML Service   │  │ User Service │
    │ (FastAPI)    │  │ (Spring Boot)│
    │ Port: 8000   │  │ Port: 8080   │
    └──────────────┘  └──────────────┘
```

### 주요 기능

- **ML Service**: 차량 가격 예측, 타이밍 분석, AI 스마트 분석
- **User Service**: 사용자 인증, 회원 관리

---

## 🔐 인증

### ML Service
- **인증 방식**: 없음 (공개 API)
- **접근 제한**: CORS 허용 (모든 도메인)

### User Service
- **인증 방식**: JWT (JSON Web Token)
- **헤더 형식**: `Authorization: Bearer {token}`
- **토큰 만료**: 24시간
- **갱신**: 로그인 재시도

#### 인증 예제
```bash
# 1. 로그인하여 토큰 획득
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'

# 응답
{
  "success": true,
  "message": "로그인 성공",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 2. 토큰으로 인증된 API 호출
curl -X GET "http://localhost:8080/api/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📦 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "message": "성공 메시지"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": "에러 타입",
  "message": "에러 메시지",
  "details": { ... }
}
```

---

## ⚠️ 에러 코드

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 400 | Bad Request | 잘못된 요청 (입력 검증 실패) |
| 401 | Unauthorized | 인증 실패 (토큰 없음/만료) |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 커스텀 에러 코드

| 에러 코드 | 설명 | 해결 방법 |
|-----------|------|----------|
| `INVALID_INPUT` | 입력 데이터 검증 실패 | 요청 데이터 확인 |
| `MODEL_NOT_FOUND` | ML 모델 파일 없음 | 모델 학습 필요 |
| `USER_NOT_FOUND` | 사용자 없음 | 이메일 확인 |
| `INVALID_CREDENTIALS` | 로그인 실패 | 비밀번호 확인 |
| `TOKEN_EXPIRED` | JWT 토큰 만료 | 재로그인 필요 |
| `DUPLICATE_EMAIL` | 이메일 중복 | 다른 이메일 사용 |

---

## 🟢 ML Service API (포트 8000)

### 1. 헬스체크

서버 상태를 확인합니다.

```
GET /api/health
```

#### 요청
```bash
curl http://localhost:8000/api/health
```

#### 응답
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "중고차 가격 예측 API가 정상 작동 중입니다"
}
```

---

### 2. 가격 예측

차량 정보를 기반으로 중고차 가격을 예측합니다.

```
POST /api/predict
```

#### 요청 본문
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린"
}
```

#### 요청 예제
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "현대",
    "model": "그랜저",
    "year": 2022,
    "mileage": 35000,
    "fuel": "가솔린"
  }'
```

#### 성공 응답 (200)
```json
{
  "predicted_price": 3200,
  "price_range": [2880, 3520],
  "confidence": 0.87
}
```

#### 에러 응답 (400)
```json
{
  "detail": {
    "error": "입력 데이터 검증 실패",
    "messages": [
      "브랜드 '현다'는 지원하지 않습니다",
      "주행거리는 0 이상이어야 합니다"
    ]
  }
}
```

#### 파라미터

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| brand | string | ✅ | 브랜드명 | "현대", "기아", "벤츠" |
| model | string | ✅ | 모델명 | "그랜저", "쏘나타" |
| year | integer | ✅ | 연식 (2000-2025) | 2022 |
| mileage | integer | ✅ | 주행거리 (km) | 35000 |
| fuel | string | ✅ | 연료 타입 | "가솔린", "디젤", "전기" |

---

### 3. 타이밍 분석

구매 적기를 분석합니다.

```
POST /api/timing
```

#### 요청 본문
```json
{
  "model": "그랜저"
}
```

#### 요청 예제
```bash
curl -X POST "http://localhost:8000/api/timing" \
  -H "Content-Type: application/json" \
  -d '{"model": "그랜저"}'
```

#### 성공 응답 (200)
```json
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

#### 파라미터

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| model | string | ✅ | 모델명 |

#### 타이밍 판단 기준

| 점수 | 판단 | 색상 | 설명 |
|------|------|------|------|
| 70-100 | 구매 적기 | 🟢 | 지금 사기 좋음 |
| 50-69 | 관망 | 🟡 | 1-2개월 후 재검토 |
| 0-49 | 대기 | 🔴 | 구매 미루기 권장 |

---

### 4. 통합 스마트 분석

가격 예측 + 타이밍 분석 + Groq AI 분석을 통합 제공합니다.

```
POST /api/smart-analysis
```

#### 요청 본문
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2022,
  "mileage": 35000,
  "fuel": "가솔린",
  "sale_price": 3200,
  "dealer_description": "완벽한 차량입니다. 무사고입니다.",
  "performance_record": {
    "accidents": 0,
    "repairs": 2
  }
}
```

#### 요청 예제
```bash
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

#### 성공 응답 (200)
```json
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
    "breakdown": {
      "macro": 78.2,
      "trend": 72.5,
      "schedule": 75.8
    },
    "reasons": [
      "✅ 저금리 2.5%",
      "✅ 관심도 안정"
    ]
  },
  "groq_analysis": {
    "signal": {
      "signal": "buy",
      "signal_text": "매수",
      "color": "🟢",
      "confidence": 85,
      "short_summary": "적정가 + 좋은 타이밍",
      "key_points": [
        "AI 예측가와 일치",
        "시장 상황 양호",
        "무사고 차량"
      ],
      "report": "현재 시장 상황과 차량 상태를 종합했을 때..."
    },
    "fraud_check": {
      "is_suspicious": false,
      "fraud_score": 20,
      "warnings": [],
      "summary": "의심스러운 점이 발견되지 않았습니다"
    },
    "negotiation": {
      "target_price": 3136,
      "discount_amount": 64,
      "message_script": "안녕하세요. 그랜저 매물에 관심있습니다...",
      "phone_script": "1. 인사 및 매물 확인\n2. 가격 협상 시작...",
      "key_arguments": [
        "AI 분석 결과 적정가는 3136만원",
        "유사 매물 비교"
      ],
      "tips": [
        "성능기록부 재확인",
        "시승 시 체크포인트"
      ]
    }
  }
}
```

#### 파라미터

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| brand | string | ✅ | 브랜드명 |
| model | string | ✅ | 모델명 |
| year | integer | ✅ | 연식 |
| mileage | integer | ✅ | 주행거리 |
| fuel | string | ✅ | 연료 타입 |
| sale_price | integer | ⭕ | 판매가 (만원) |
| dealer_description | string | ⭕ | 딜러 설명글 |
| performance_record | object | ⭕ | 성능기록부 |

**주의**: Groq AI 기능은 `GROQ_API_KEY` 설정 시에만 작동합니다.

---

### 5. 브랜드 목록 조회

지원하는 차량 브랜드 목록을 반환합니다.

```
GET /api/brands
```

#### 요청 예제
```bash
curl http://localhost:8000/api/brands
```

#### 성공 응답 (200)
```json
{
  "brands": [
    "현대", "기아", "제네시스", "벤츠", "BMW", "아우디",
    "폭스바겐", "볼보", "푸조", "시트로엥", "르노", "미니",
    "렉서스", "토요타", "혼다", "닛산", "인피니티", "마쓰다",
    "쉐보레", "포드", "지프", "링컨", "캐딜락", "테슬라",
    "포르쉐", "재규어", "랜드로버", "벤틀리", "롤스로이스",
    "애스턴마틴", "람보르기니", "페라리"
  ]
}
```

---

### 6. 브랜드별 모델 목록 조회

특정 브랜드의 모델 목록을 반환합니다.

```
GET /api/models/{brand}
```

#### 요청 예제
```bash
# 현대 브랜드
curl http://localhost:8000/api/models/현대

# 기아 브랜드
curl http://localhost:8000/api/models/기아
```

#### 성공 응답 (200)
```json
{
  "brand": "현대",
  "models": [
    "그랜저", "쏘나타", "아반떼", "투싼",
    "팰리세이드", "산타페", "코나", "벨로스터"
  ]
}
```

#### 브랜드 없음 (200)
```json
{
  "brand": "알수없음",
  "models": []
}
```

---

### 7. 연료 타입 목록 조회

지원하는 연료 타입 목록을 반환합니다.

```
GET /api/fuel-types
```

#### 요청 예제
```bash
curl http://localhost:8000/api/fuel-types
```

#### 성공 응답 (200)
```json
{
  "fuel_types": [
    "가솔린",
    "디젤",
    "LPG",
    "하이브리드",
    "전기",
    "가솔린+LPG",
    "가솔린+전기",
    "수소"
  ]
}
```

---

## 🔵 User Service API (포트 8080)

### 1. 헬스체크

서버 상태를 확인합니다.

```
GET /api/auth/health
```

#### 요청 예제
```bash
curl http://localhost:8080/api/auth/health
```

#### 성공 응답 (200)
```json
{
  "status": "healthy",
  "message": "Spring Boot User Management API",
  "version": "1.0.0"
}
```

---

### 2. 회원가입

새로운 사용자를 등록합니다.

```
POST /api/auth/signup
```

#### 요청 본문
```json
{
  "username": "홍길동",
  "email": "hong@example.com",
  "password": "Password123!",
  "phoneNumber": "010-1234-5678"
}
```

#### 요청 예제
```bash
curl -X POST "http://localhost:8080/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "홍길동",
    "email": "hong@example.com",
    "password": "Password123!",
    "phoneNumber": "010-1234-5678"
  }'
```

#### 성공 응답 (200)
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다",
  "user": {
    "id": 1,
    "username": "홍길동",
    "email": "hong@example.com",
    "phoneNumber": "010-1234-5678",
    "role": "USER",
    "createdAt": "2025-11-24T10:30:00"
  }
}
```

#### 에러 응답 (400)
```json
{
  "success": false,
  "message": "이미 사용 중인 이메일입니다"
}
```

#### 파라미터

| 필드 | 타입 | 필수 | 제약 조건 |
|------|------|------|-----------|
| username | string | ✅ | 2-50자, 중복 불가 |
| email | string | ✅ | 이메일 형식, 중복 불가 |
| password | string | ✅ | 8자 이상, 영문+숫자+특수문자 |
| phoneNumber | string | ⭕ | 010-0000-0000 형식 |

**비밀번호 규칙**:
- 최소 8자
- 영문자 포함
- 숫자 포함
- 특수문자 포함 (@$!%*#?&)

---

### 3. 로그인

사용자 인증 후 JWT 토큰을 발급합니다.

```
POST /api/auth/login
```

#### 요청 본문
```json
{
  "email": "hong@example.com",
  "password": "Password123!"
}
```

#### 요청 예제
```bash
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hong@example.com",
    "password": "Password123!"
  }'
```

#### 성공 응답 (200)
```json
{
  "success": true,
  "message": "로그인 성공",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJob25nQGV4YW1wbGUuY29tIiwiaWF0IjoxNjMyNDQ4MDAwLCJleHAiOjE2MzI1MzQ0MDB9.signature"
}
```

#### 에러 응답 (401)
```json
{
  "success": false,
  "message": "이메일 또는 비밀번호가 올바르지 않습니다"
}
```

---

### 4. 내 정보 조회

로그인한 사용자의 정보를 조회합니다.

```
GET /api/auth/me
🔒 인증 필요
```

#### 요청 예제
```bash
curl -X GET "http://localhost:8080/api/auth/me" \
  -H "Authorization: Bearer {your_token}"
```

#### 성공 응답 (200)
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "홍길동",
    "email": "hong@example.com",
    "phoneNumber": "010-1234-5678",
    "role": "USER",
    "createdAt": "2025-11-24T10:30:00"
  }
}
```

#### 에러 응답 (401)
```json
{
  "success": false,
  "message": "인증이 필요합니다"
}
```

---

### 5. 회원 정보 수정

사용자 정보를 수정합니다.

```
PUT /api/auth/update
🔒 인증 필요
```

#### 요청 본문
```json
{
  "username": "홍길동2",
  "phoneNumber": "010-9999-8888"
}
```

#### 요청 예제
```bash
curl -X PUT "http://localhost:8080/api/auth/update" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "홍길동2",
    "phoneNumber": "010-9999-8888"
  }'
```

#### 성공 응답 (200)
```json
{
  "success": true,
  "message": "회원 정보가 수정되었습니다",
  "user": {
    "id": 1,
    "username": "홍길동2",
    "email": "hong@example.com",
    "phoneNumber": "010-9999-8888",
    "role": "USER"
  }
}
```

---

### 6. 회원 탈퇴

사용자 계정을 비활성화합니다 (소프트 삭제).

```
DELETE /api/auth/delete
🔒 인증 필요
```

#### 요청 예제
```bash
curl -X DELETE "http://localhost:8080/api/auth/delete" \
  -H "Authorization: Bearer {your_token}"
```

#### 성공 응답 (200)
```json
{
  "success": true,
  "message": "회원 탈퇴가 완료되었습니다"
}
```

---

## 📊 데이터 모델

### PredictRequest
```typescript
{
  brand: string;        // 브랜드명
  model: string;        // 모델명
  year: number;         // 연식 (2000-2025)
  mileage: number;      // 주행거리 (km)
  fuel: string;         // 연료 타입
}
```

### PredictResponse
```typescript
{
  predicted_price: number;    // 예측 가격 (만원)
  price_range: [number, number];  // [최소, 최대]
  confidence: number;         // 신뢰도 (0-1)
}
```

### TimingResponse
```typescript
{
  timing_score: number;       // 타이밍 점수 (0-100)
  decision: string;           // 판단 결과
  color: string;              // 신호등 색상
  breakdown: {
    macro: number;            // 거시경제 점수
    trend: number;            // 트렌드 점수
    schedule: number;         // 신차 일정 점수
  };
  reasons: string[];          // 판단 근거
}
```

### UserSignupDto
```typescript
{
  username: string;           // 사용자명 (2-50자)
  email: string;              // 이메일
  password: string;           // 비밀번호 (8자 이상)
  phoneNumber?: string;       // 전화번호 (선택)
}
```

### UserResponseDto
```typescript
{
  id: number;                 // 사용자 ID
  username: string;           // 사용자명
  email: string;              // 이메일
  phoneNumber: string;        // 전화번호
  role: string;               // 권한 (USER/ADMIN)
  createdAt: string;          // 생성일시
}
```

---

## 🎬 통합 시나리오

### 시나리오 1: 신규 사용자 차량 구매 프로세스

```javascript
// Step 1: 회원가입
const signupResponse = await fetch('http://localhost:8080/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: '김철수',
    email: 'kim@example.com',
    password: 'Password123!',
    phoneNumber: '010-1234-5678'
  })
});

// Step 2: 로그인
const loginResponse = await fetch('http://localhost:8080/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'kim@example.com',
    password: 'Password123!'
  })
});
const { token } = await loginResponse.json();

// Step 3: 브랜드 목록 조회
const brandsResponse = await fetch('http://localhost:8000/api/brands');
const { brands } = await brandsResponse.json();
// ["현대", "기아", ...]

// Step 4: 현대 브랜드의 모델 목록 조회
const modelsResponse = await fetch('http://localhost:8000/api/models/현대');
const { models } = await modelsResponse.json();
// ["그랜저", "쏘나타", ...]

// Step 5: 가격 예측
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
// { predicted_price: 3200, ... }

// Step 6: 통합 스마트 분석
const smartResponse = await fetch('http://localhost:8000/api/smart-analysis', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    brand: '현대',
    model: '그랜저',
    year: 2022,
    mileage: 35000,
    fuel: '가솔린',
    sale_price: 3200,
    dealer_description: '완벽한 차량입니다.'
  })
});
const smartAnalysis = await smartResponse.json();
// { prediction: {...}, timing: {...}, groq_analysis: {...} }
```

---

## 📝 버전 히스토리

### v1.0.0 (2025-11-24)
- ✅ ML Service 7개 API 구현
- ✅ User Service 6개 API 구현
- ✅ JWT 인증 시스템
- ✅ Groq AI 통합 (신호등, 허위매물, 네고)
- ✅ 마이크로서비스 아키텍처 구축
- ✅ API 문서 자동 생성 (Swagger/ReDoc)

### 향후 계획
- 🔜 v1.1.0: 차량 비교 기능
- 🔜 v1.2.0: 검색 히스토리 저장
- 🔜 v1.3.0: 알림 기능
- 🔜 v2.0.0: GraphQL 지원

---

## 🔗 관련 링크

- **GitHub**: https://github.com/your-username/used-car-price-predictor
- **Swagger UI (ML)**: http://localhost:8000/docs
- **ReDoc (ML)**: http://localhost:8000/redoc
- **마이크로서비스 가이드**: [MICROSERVICES_GUIDE.md](MICROSERVICES_GUIDE.md)
- **User Service 설정**: [user-service/SETUP_GUIDE.md](user-service/SETUP_GUIDE.md)
- **ML Service 가이드**: [ml-service/README.md](ml-service/README.md)

---

## 📞 문의 및 지원

- **이슈 등록**: GitHub Issues
- **기여 가이드**: CONTRIBUTING.md
- **라이센스**: MIT License

---

**© 2025 중고차 가격 예측 시스템 - All Rights Reserved**

