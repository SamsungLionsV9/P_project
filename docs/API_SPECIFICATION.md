# API 명세서

## 개요

| 서비스 | 기본 URL | 설명 |
|--------|----------|------|
| ML Service | `http://localhost:5001` | 가격 예측, 분석 API |
| User Service | `http://localhost:8080/api` | 인증, 사용자 관리 API |

---

## ML Service API

### 1. 가격 예측

**POST** `/predict`

중고차 가격을 예측합니다.

**Request Body**:
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2020,
  "mileage": 50000,
  "fuel": "가솔린",
  "accident_free": true,
  "options": {
    "sunroof": true,
    "navigation": true,
    "smart_key": true
  }
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "predicted_price": 28500000,
  "price_range": {
    "min": 25650000,
    "max": 31350000
  },
  "confidence": 0.85,
  "factors": {
    "year_impact": -0.15,
    "mileage_impact": -0.08,
    "options_impact": 0.05
  }
}
```

### 2. 타이밍 분석

**POST** `/timing`

구매/판매 타이밍을 분석합니다.

**Request Body**:
```json
{
  "brand": "현대",
  "model": "그랜저"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "timing_score": 75,
  "recommendation": "buy",
  "factors": {
    "seasonality": {"score": 80, "description": "비수기로 가격 하락 예상"},
    "new_car_release": {"score": 70, "description": "신모델 출시 6개월 후"},
    "market_trend": {"score": 75, "description": "시장 가격 안정세"}
  },
  "best_timing": "2025년 1-2월",
  "price_forecast": {
    "current": 28500000,
    "expected_3m": 27800000,
    "change_rate": -2.5
  }
}
```

### 3. 유사 차량 검색

**POST** `/similar`

유사 조건의 실매물을 검색합니다.

**Request Body**:
```json
{
  "brand": "현대",
  "model": "그랜저",
  "year": 2020,
  "mileage": 50000,
  "predicted_price": 28500000
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "similar_count": 45,
  "price_distribution": {
    "min": 24000000,
    "max": 32000000,
    "median": 27500000,
    "avg": 27800000
  },
  "comparison": {
    "below_predicted": 28,
    "above_predicted": 17,
    "good_deals": 5
  }
}
```

### 4. 브랜드/모델 목록

**GET** `/brands`

지원하는 브랜드 목록을 반환합니다.

**Response** `200 OK`:
```json
{
  "domestic": ["현대", "기아", "제네시스", "쉐보레", "르노코리아", "KG모빌리티"],
  "imported": ["BMW", "벤츠", "아우디", "폭스바겐", "볼보", "렉서스", "토요타", "혼다"]
}
```

**GET** `/models?brand={brand}`

해당 브랜드의 모델 목록을 반환합니다.

**Response** `200 OK`:
```json
{
  "brand": "현대",
  "models": ["그랜저", "쏘나타", "아반떼", "싼타페", "투싼", "팰리세이드"]
}
```

---

## User Service API

### 1. 이메일 인증 코드 발송

**POST** `/api/auth/email/send-code`

이메일로 6자리 인증 코드를 발송합니다.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "인증 코드가 발송되었습니다. 이메일을 확인해주세요."
}
```

### 2. 이메일 인증 코드 확인

**POST** `/api/auth/email/verify-code`

발송된 인증 코드를 확인합니다.

**Request Body**:
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "이메일 인증이 완료되었습니다"
}
```

### 3. 회원가입

**POST** `/api/auth/signup`

새 계정을 생성합니다. (이메일 인증 필수)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "홍길동"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "홍길동"
  }
}
```

### 4. 로그인

**POST** `/api/auth/login`

이메일/비밀번호로 로그인합니다.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "홍길동"
  }
}
```

### 5. 소셜 로그인

**GET** `/oauth2/authorization/{provider}`

OAuth2 소셜 로그인을 시작합니다.

| Provider | URL |
|----------|-----|
| 네이버 | `/oauth2/authorization/naver` |
| 카카오 | `/oauth2/authorization/kakao` |
| 구글 | `/oauth2/authorization/google` |

**성공 시 리다이렉트**:
```
/oauth2/callback?token={jwt_token}&email={user_email}&provider={provider}
```

### 6. 현재 사용자 정보

**GET** `/api/auth/me`

현재 로그인한 사용자 정보를 조회합니다.

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "홍길동",
  "provider": "email",
  "createdAt": "2025-11-26T12:00:00"
}
```

---

## 에러 응답

모든 API는 다음 형식의 에러 응답을 반환합니다:

```json
{
  "success": false,
  "message": "에러 메시지",
  "errorCode": "ERROR_CODE"
}
```

| HTTP 코드 | 설명 |
|-----------|------|
| 400 | 잘못된 요청 (유효성 검증 실패) |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 내부 오류 |

---

*Last Updated: 2025-11-26*
