# 🔐 소셜 로그인 설정 가이드

## 지원 소셜 로그인
- **Google** (구글)
- **Naver** (네이버)
- **Kakao** (카카오)

---

## 1️⃣ Google OAuth2 설정

### 1. [Google Cloud Console](https://console.cloud.google.com/) 접속

### 2. 프로젝트 생성/선택

### 3. OAuth 동의 화면 설정
- **User Type**: 외부
- **앱 이름**: 중고차 가격 예측
- **사용자 지원 이메일**: 본인 이메일
- **범위**: email, profile

### 4. 사용자 인증 정보 생성
- **OAuth 2.0 클라이언트 ID** 생성
- **애플리케이션 유형**: 웹 애플리케이션
- **승인된 리디렉션 URI**: 
  ```
  http://localhost:8080/login/oauth2/code/google
  ```

### 5. 환경변수 설정
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

---

## 2️⃣ Naver OAuth2 설정

### 1. [Naver Developers](https://developers.naver.com/) 접속

### 2. 애플리케이션 등록
- **애플리케이션 이름**: 중고차 가격 예측
- **사용 API**: 네이버 로그인

### 3. API 설정
- **서비스 URL**: `http://localhost:8080`
- **네이버 로그인 Callback URL**:
  ```
  http://localhost:8080/login/oauth2/code/naver
  ```

### 4. 필수 정보 선택
- 이름 ✅
- 이메일 ✅
- 프로필 사진 ✅

### 5. 환경변수 설정
```bash
export NAVER_CLIENT_ID="your-client-id"
export NAVER_CLIENT_SECRET="your-client-secret"
```

---

## 3️⃣ Kakao OAuth2 설정

### 1. [Kakao Developers](https://developers.kakao.com/) 접속

### 2. 애플리케이션 생성
- **앱 이름**: 중고차 가격 예측

### 3. 플랫폼 등록
- **Web**: `http://localhost:8080`

### 4. 카카오 로그인 활성화
- **카카오 로그인** > **활성화 설정**: ON
- **Redirect URI**:
  ```
  http://localhost:8080/login/oauth2/code/kakao
  ```

### 5. 동의항목 설정
- 닉네임 ✅ (필수)
- 카카오계정(이메일) ✅ (선택 → 필수로 변경 권장)

### 6. 보안 > Client Secret 생성
- **코드 생성** 클릭

### 7. 환경변수 설정
```bash
export KAKAO_CLIENT_ID="your-rest-api-key"
export KAKAO_CLIENT_SECRET="your-client-secret"
```

---

## 📝 application.yml 설정

환경변수 대신 직접 설정할 경우:

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: your-google-client-id
            client-secret: your-google-client-secret
          naver:
            client-id: your-naver-client-id
            client-secret: your-naver-client-secret
          kakao:
            client-id: your-kakao-client-id
            client-secret: your-kakao-client-secret
```

---

## 🔗 소셜 로그인 URL

| 제공자 | 로그인 URL |
|--------|-----------|
| Google | `http://localhost:8080/oauth2/authorization/google` |
| Naver | `http://localhost:8080/oauth2/authorization/naver` |
| Kakao | `http://localhost:8080/oauth2/authorization/kakao` |

---

## 🔄 로그인 플로우

```
1. 사용자 → 소셜 로그인 URL 접속
2. 소셜 제공자 로그인 페이지
3. 사용자 동의 → 인증 코드 발급
4. 서버에서 액세스 토큰 교환
5. 사용자 정보 조회
6. JWT 토큰 발급
7. 프론트엔드로 리다이렉트 (토큰 포함)
```

### 성공 시 리다이렉트
```
http://localhost:3000/oauth2/redirect?token=JWT_TOKEN&email=user@email.com&provider=GOOGLE
```

### 실패 시 리다이렉트
```
http://localhost:3000/oauth2/redirect?error=에러메시지
```

---

## 🗄️ DB 스키마 업데이트

소셜 로그인 지원을 위해 users 테이블에 컬럼이 추가됨:

```sql
-- 추가된 컬럼
provider VARCHAR(20)        -- LOCAL, GOOGLE, NAVER, KAKAO
provider_id VARCHAR(100)    -- 소셜 로그인 제공자의 사용자 ID
profile_image_url VARCHAR(500)  -- 프로필 이미지 URL

-- password는 nullable로 변경 (소셜 로그인은 비밀번호 없음)
```

스키마 업데이트 SQL:
```bash
mysql -u root -p car_database < setup/oauth2_schema_update.sql
```

---

## ⚠️ 주의사항

1. **운영 환경**에서는 반드시 환경변수로 설정
2. **HTTPS** 사용 권장 (특히 운영 환경)
3. **Redirect URI**는 등록된 것만 허용됨
4. 각 소셜 서비스의 **개인정보 처리방침** 필요

---

## 🧪 테스트

```bash
# 구글 로그인 테스트
open http://localhost:8080/oauth2/authorization/google

# 네이버 로그인 테스트
open http://localhost:8080/oauth2/authorization/naver

# 카카오 로그인 테스트
open http://localhost:8080/oauth2/authorization/kakao
```

