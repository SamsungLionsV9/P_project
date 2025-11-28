# 🎉 소셜 로그인 구현 완료 (2025-11-25)

## ✅ 구현 완료된 소셜 로그인

| 플랫폼 | 상태 | 테스트 결과 |
|--------|------|-------------|
| **카카오** | ✅ 완료 | JWT 토큰 발급 성공 |
| **구글** | ✅ 완료 | JWT 토큰 발급 성공 |
| **네이버** | ✅ 완료 | JWT 토큰 발급 성공 |

---

## 🔗 소셜 로그인 URL

```
카카오: http://localhost:8080/oauth2/authorization/kakao
구글:   http://localhost:8080/oauth2/authorization/google
네이버: http://localhost:8080/oauth2/authorization/naver
```

---

## 📋 로그인 성공 시 응답

### 리다이렉트 URL
```
http://localhost:3000/oauth2/redirect?token=JWT토큰&email=사용자이메일&provider=제공자
```

### JWT 토큰 내용 (예시)
```json
{
  "id": 3,
  "email": "user@example.com",
  "role": "USER",
  "provider": "GOOGLE",
  "iat": 1764054824,
  "exp": 1764141224
}
```

---

## 🗂️ 구현된 파일들

### 1. 설정 파일
- `user-service/src/main/resources/application.yml` - OAuth2 설정

### 2. OAuth2 관련 클래스
```
user-service/src/main/java/com/example/carproject/oauth2/
├── CustomOAuth2UserService.java      # OAuth2 사용자 서비스
├── OAuth2AuthenticationSuccessHandler.java  # 로그인 성공 핸들러
├── OAuth2AuthenticationFailureHandler.java  # 로그인 실패 핸들러
├── OAuth2UserInfo.java               # 사용자 정보 추상 클래스
├── GoogleOAuth2UserInfo.java         # 구글 사용자 정보
├── NaverOAuth2UserInfo.java          # 네이버 사용자 정보
└── KakaoOAuth2UserInfo.java          # 카카오 사용자 정보
```

### 3. 수정된 파일
- `user-service/build.gradle` - OAuth2 의존성 추가
- `user-service/.../entity/User.java` - 소셜 로그인 필드 추가
- `user-service/.../config/SecurityConfig.java` - OAuth2 설정 추가

---

## 🗄️ DB 스키마 변경

소셜 로그인을 위해 users 테이블에 컬럼 추가:

```sql
ALTER TABLE users ADD COLUMN provider VARCHAR(20) DEFAULT 'LOCAL';
ALTER TABLE users ADD COLUMN provider_id VARCHAR(100);
ALTER TABLE users ADD COLUMN profile_image_url VARCHAR(500);
ALTER TABLE users MODIFY password VARCHAR(255) NULL;
```

---

## 🎯 프론트엔드 연동 가이드

### 1. 로그인 버튼 구현
```html
<button onclick="location.href='http://localhost:8080/oauth2/authorization/kakao'">
  카카오 로그인
</button>
<button onclick="location.href='http://localhost:8080/oauth2/authorization/google'">
  구글 로그인
</button>
<button onclick="location.href='http://localhost:8080/oauth2/authorization/naver'">
  네이버 로그인
</button>
```

### 2. 리다이렉트 페이지 (/oauth2/redirect)
```javascript
// URL에서 토큰 추출
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const email = params.get('email');
const provider = params.get('provider');

if (token) {
  // 토큰 저장
  localStorage.setItem('accessToken', token);
  localStorage.setItem('userEmail', email);
  localStorage.setItem('provider', provider);
  
  // 메인 페이지로 이동
  window.location.href = '/';
} else {
  // 에러 처리
  const error = params.get('error');
  alert('로그인 실패: ' + error);
}
```

### 3. API 호출 시 토큰 사용
```javascript
// Authorization 헤더에 토큰 포함
fetch('http://localhost:8080/api/users/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## ⚙️ 환경별 설정

### 개발 환경 (localhost)
- Redirect URI: `http://localhost:8080/login/oauth2/code/{provider}`
- Frontend URL: `http://localhost:3000`

### 운영 환경 (배포 시)
- Redirect URI: `https://your-domain.com/login/oauth2/code/{provider}`
- Frontend URL: `https://your-frontend-domain.com`
- 각 소셜 로그인 콘솔에서 운영 URL 등록 필요

---

## 🔐 보안 권장사항

1. **운영 환경**에서는 Client ID/Secret을 환경변수로 관리
2. **HTTPS** 필수 사용
3. JWT Secret Key는 충분히 긴 값 사용 (256bit 이상)
4. 토큰 만료 시간 적절히 설정 (현재 24시간)

---

## 📞 API 키 발급처

| 플랫폼 | 개발자 콘솔 |
|--------|-------------|
| 카카오 | https://developers.kakao.com |
| 구글 | https://console.cloud.google.com |
| 네이버 | https://developers.naver.com |

---

## ✅ 테스트 완료 항목

- [x] 카카오 로그인 → JWT 토큰 발급
- [x] 구글 로그인 → JWT 토큰 발급  
- [x] 네이버 로그인 → JWT 토큰 발급
- [x] DB에 소셜 로그인 사용자 저장
- [x] 중복 로그인 시 기존 사용자 정보 업데이트
- [ ] 프론트엔드 연동 (프론트엔드 개발 후 진행)

---

## 📝 작업자
- 작업일: 2025-11-25
- 작업 내용: 카카오, 구글, 네이버 소셜 로그인 구현 완료

