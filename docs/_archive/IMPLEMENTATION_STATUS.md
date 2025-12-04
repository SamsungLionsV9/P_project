# 구현 현황 및 TODO

> 최종 업데이트: 2025-11-26

---

## 1. 현재 구현 현황

### Frontend (Flutter)

| 기능 | 파일 | 상태 | 백엔드 연동 |
|------|------|------|------------|
| 홈 화면 | `main.dart` | ✅ 완료 | - |
| 로그인 UI | `main.dart` | ✅ 완료 | ✅ User Service |
| 회원가입 | `signup_page.dart` | ✅ 완료 | ✅ User Service |
| 이메일 인증 | `signup_page.dart` | ✅ 완료 | ✅ User Service |
| 소셜 로그인 WebView | `oauth_webview_page.dart` | ✅ 완료 | ⚠️ 설정 필요 |
| 차량 정보 입력 | `car_info_input_page.dart` | ✅ 완료 | ✅ ML Service |
| 예측 결과 | `result_page.dart` | ✅ 완료 | ✅ ML Service |
| 추천 페이지 | `recommendation_page.dart` | ✅ 완료 | ✅ ML Service |
| 마이페이지 | `mypage.dart` | ✅ 완료 | ✅ ML Service |
| 설정 | `settings_page.dart` | ✅ 완료 | - |

### Backend - ML Service (Python/FastAPI :8001)

| API | 엔드포인트 | 상태 | 설명 |
|-----|-----------|------|------|
| 가격 예측 | `POST /api/predict` | ✅ 완료 | XGBoost v12/v14 |
| 타이밍 분석 | `POST /api/timing` | ✅ 완료 | 구매 타이밍 점수 |
| 유사 차량 | `POST /api/similar` | ✅ 완료 | 가격 분포 분석 |
| AI 분석 | `POST /api/smart-analysis` | ✅ 완료 | Groq AI 통합 |
| 인기 모델 | `GET /api/popular` | ✅ 완료 | 엔카 데이터 기반 |
| 트렌딩 | `GET /api/trending` | ✅ 완료 | 최근 검색 기반 |
| 추천 차량 | `GET /api/recommendations` | ✅ 완료 | 예산별 추천 |
| 급매물 | `GET /api/good-deals` | ✅ 완료 | 가성비 차량 |
| 검색 이력 | `GET/POST /api/history` | ✅ 완료 | SQLite 저장 |
| 즐겨찾기 | `GET/POST/DELETE /api/favorites` | ✅ 완료 | SQLite 저장 |
| 가격 알림 | `GET/POST/DELETE /api/alerts` | ✅ 완료 | SQLite 저장 |
| 브랜드/모델 | `GET /api/brands`, `/api/models` | ✅ 완료 | 정적 데이터 |

### Backend - User Service (Spring Boot :8080)

| API | 엔드포인트 | 상태 | 설명 |
|-----|-----------|------|------|
| 헬스체크 | `GET /api/auth/health` | ✅ 완료 | |
| 회원가입 | `POST /api/auth/signup` | ✅ 완료 | 이메일 인증 필수 |
| 로그인 | `POST /api/auth/login` | ✅ 완료 | JWT 토큰 발급 |
| 이메일 인증 발송 | `POST /api/auth/email/send-code` | ✅ 완료 | 6자리 코드 |
| 이메일 인증 확인 | `POST /api/auth/email/verify-code` | ✅ 완료 | 5분 유효 |
| 현재 사용자 | `GET /api/auth/me` | ✅ 완료 | JWT 필요 |
| 네이버 로그인 | `GET /oauth2/authorization/naver` | ⚠️ 설정 필요 | 개발자 콘솔 |
| 카카오 로그인 | `GET /oauth2/authorization/kakao` | ⚠️ 설정 필요 | 개발자 콘솔 |
| 구글 로그인 | `GET /oauth2/authorization/google` | ⚠️ 설정 필요 | Private IP 제한 |

---

## 2. 알려진 문제점

### 🔴 Critical

| 문제 | 설명 | 영향 |
|------|------|------|
| **포트 불일치** | ApiService는 8001, AuthService는 8080 | 서비스 분리됨 |
| **사용자 식별 하드코딩** | ML Service에서 `user_id="guest"` 고정 | 사용자별 데이터 분리 불가 |
| **JWT 미연동** | 로그인 후 토큰이 ML Service로 전달 안됨 | 인증된 요청 불가 |

### 🟡 Warning

| 문제 | 설명 |
|------|------|
| 소셜 로그인 미작동 | 네이버/카카오/구글 개발자 콘솔 설정 필요 |
| 구글 Private IP 제한 | 에뮬레이터(10.0.2.2)에서 구글 OAuth 불가 |
| 이메일 발송 미설정 | SMTP 설정 없이는 콘솔 로그로만 확인 |

---

## 3. 구현 TODO 목록

### Phase 1: 서비스 통합 (우선순위 높음)

- [ ] **JWT 토큰 전달 통합**
  - Flutter: 로그인 후 토큰 저장 (SharedPreferences)
  - ML Service: JWT 검증 미들웨어 추가
  - 모든 API 요청에 Authorization 헤더 추가

- [ ] **사용자별 데이터 분리**
  - ML Service: `user_id` 파라미터를 JWT에서 추출
  - DB 스키마에 user_id 외래키 추가

- [ ] **API Gateway 통합** (선택)
  - User Service가 ML Service를 프록시
  - 단일 엔드포인트로 통합

### Phase 2: 소셜 로그인 완성

- [ ] **네이버 개발자 콘솔 설정**
  - 서비스 URL: `http://localhost:8080`
  - Callback URL: `http://localhost:8080/login/oauth2/code/naver`
  - 테스터 ID 등록

- [ ] **카카오 개발자 콘솔 설정**
  - Kakao Login 활성화
  - Redirect URI 등록
  - 팀원 등록

- [ ] **구글 OAuth 개선**
  - 실제 도메인 배포 후 테스트
  - 또는 ngrok 터널링 사용

### Phase 3: 기능 개선

- [ ] **실시간 알림**
  - FCM(Firebase Cloud Messaging) 연동
  - 가격 알림 푸시 알림

- [ ] **검색 자동완성**
  - 브랜드/모델 입력 시 자동완성
  - 최근 검색어 표시

- [ ] **차량 비교 기능**
  - 여러 차량 동시 비교
  - 비교 결과 저장

- [ ] **공유 기능**
  - 예측 결과 이미지 공유
  - 딥링크 지원

### Phase 4: 운영 준비

- [ ] **에러 처리 강화**
  - 전역 에러 핸들러
  - 사용자 친화적 에러 메시지

- [ ] **로깅 시스템**
  - 구조화된 로그 (JSON)
  - 로그 수집/분석 (ELK Stack)

- [ ] **배포 자동화**
  - Docker 컨테이너화
  - CI/CD 파이프라인

---

## 4. 개선 TODO 목록

### UI/UX 개선

| 항목 | 현재 | 개선 방향 |
|------|------|----------|
| 로딩 상태 | 기본 CircularProgress | Shimmer 효과, 스켈레톤 UI |
| 에러 화면 | 텍스트만 표시 | 재시도 버튼, 친화적 메시지 |
| 애니메이션 | 기본 | Hero 애니메이션, 페이지 전환 |
| 다크 모드 | 부분 지원 | 완전한 다크 모드 |

### 성능 개선

| 항목 | 현재 | 개선 방향 |
|------|------|----------|
| API 캐싱 | 없음 | 브랜드/모델 목록 캐싱 |
| 이미지 | 없음 | 차량 이미지 추가 + 캐싱 |
| 모델 로딩 | 매 요청 | 서버 시작 시 1회 로딩 (완료) |
| DB 쿼리 | SQLite | PostgreSQL 마이그레이션 |

### 보안 강화

| 항목 | 현재 | 개선 방향 |
|------|------|----------|
| API 인증 | 부분적 | 전체 API JWT 인증 |
| Rate Limiting | 없음 | IP/사용자별 요청 제한 |
| 입력 검증 | 기본 | 서버 사이드 강화 |
| HTTPS | 개발용 HTTP | 운영 시 HTTPS 필수 |

---

## 5. 즉시 실행 가능한 작업

### 오늘 할 수 있는 것

```bash
# 1. JWT 토큰 저장 구현 (Flutter)
# AuthService에서 로그인 성공 시 SharedPreferences에 토큰 저장

# 2. ML Service에 인증 미들웨어 추가
# JWT 토큰 검증 후 user_id 추출

# 3. Flutter ApiService에 토큰 헤더 추가
# 모든 요청에 Authorization: Bearer {token} 추가
```

### 다음 우선순위

1. ✅ 이메일 인증 회원가입 → **완료**
2. 🔄 JWT 토큰 통합 → **진행 필요**
3. ⏳ 소셜 로그인 콘솔 설정 → **외부 작업**
4. ⏳ 사용자별 데이터 분리 → **DB 변경 필요**

---

*이 문서는 프로젝트 진행에 따라 업데이트됩니다.*
