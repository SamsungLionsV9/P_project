# 시스템 아키텍처

## 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flutter App                               │
│                    (Android / iOS / Web)                         │
└─────────────────────┬───────────────────────────────┬───────────┘
                      │                               │
                      ▼                               ▼
┌─────────────────────────────────┐   ┌─────────────────────────────┐
│      User Service (8080)        │   │     ML Service (5001)       │
│         Spring Boot             │   │         FastAPI             │
├─────────────────────────────────┤   ├─────────────────────────────┤
│ • 회원가입/로그인               │   │ • 가격 예측 API             │
│ • OAuth2 소셜 로그인            │   │ • 타이밍 분석 API           │
│ • 이메일 인증                   │   │ • 유사 차량 검색 API        │
│ • JWT 토큰 발급                 │   │ • 추천 서비스 API           │
└─────────────────────┬───────────┘   └─────────────────────────────┘
                      │                               │
                      ▼                               ▼
              ┌───────────────┐               ┌───────────────┐
              │   MySQL/H2    │               │  ML Models    │
              │   Database    │               │  (pkl files)  │
              └───────────────┘               └───────────────┘
```

## 서비스별 상세

### 1. ML Service (Python/FastAPI)

**포트**: 5001

**역할**: 머신러닝 기반 가격 예측 및 분석

| 모듈 | 파일 | 설명 |
|------|------|------|
| 가격 예측 | `prediction_v12.py` | 국내차/수입차 가격 예측 |
| 타이밍 분석 | `timing.py` | 구매/판매 타이밍 점수 계산 |
| 유사 차량 | `similar_service.py` | 실매물 기반 가격 분포 분석 |
| 추천 시스템 | `recommendation_service.py` | 검색 이력, 즐겨찾기, 알림 관리 |

**모델 파일 구조**:
```
models/
├── domestic_v12.pkl              # 국내차 모델
├── domestic_v12_encoders.pkl     # 인코더
├── domestic_v12_features.pkl     # 피처 목록
├── imported_v14.pkl              # 수입차 모델
├── imported_v14_encoders.pkl
└── imported_v14_features.pkl
```

### 2. User Service (Java/Spring Boot)

**포트**: 8080

**역할**: 사용자 인증 및 데이터 관리

| 패키지 | 설명 |
|--------|------|
| `controller` | REST API 엔드포인트 |
| `service` | 비즈니스 로직 |
| `repository` | JPA 데이터 접근 |
| `entity` | 데이터베이스 엔티티 |
| `oauth2` | OAuth2 소셜 로그인 처리 |
| `security` | JWT 인증 필터 |

**주요 엔티티**:
```
User                  # 사용자 정보
EmailVerification     # 이메일 인증 코드
DomesticCarDetails    # 국내차 데이터
ImportedCarDetails    # 수입차 데이터
```

### 3. Flutter App

**역할**: 크로스 플랫폼 모바일 앱

| 화면 | 파일 | 설명 |
|------|------|------|
| 홈 | `main.dart` | 로그인/회원가입, 바로가기 |
| 차량 검색 | `car_info_input_page.dart` | 가격 조회 폼 |
| 예측 결과 | `prediction_result_page.dart` | 예측 결과 상세 |
| 추천 | `recommendation_page.dart` | 인기 차량, 급매물 |
| 마이페이지 | `mypage.dart` | 검색 이력, 즐겨찾기 |
| 설정 | `settings_page.dart` | 앱 설정 |

## 인증 흐름

### 이메일 회원가입

```
[Flutter App]                [User Service]               [DB]
     │                             │                        │
     │─── POST /email/send-code ──▶│                        │
     │                             │─── 인증코드 저장 ──────▶│
     │◀── 인증코드 발송 완료 ──────│                        │
     │                             │                        │
     │─── POST /email/verify-code ▶│                        │
     │                             │─── 코드 검증 ─────────▶│
     │◀── 인증 완료 ──────────────│                        │
     │                             │                        │
     │─── POST /signup ───────────▶│                        │
     │                             │─── 회원 정보 저장 ────▶│
     │◀── JWT 토큰 반환 ──────────│                        │
```

### OAuth2 소셜 로그인

```
[Flutter App]     [User Service]      [OAuth Provider]       [DB]
     │                  │                    │                 │
     │── WebView 열기 ─▶│                    │                 │
     │                  │── 인증 요청 ──────▶│                 │
     │                  │◀── 인증 코드 ──────│                 │
     │                  │── 토큰 교환 ──────▶│                 │
     │                  │◀── Access Token ──│                 │
     │                  │── 사용자 정보 ───▶│                 │
     │                  │◀── Profile ───────│                 │
     │                  │                    │                 │
     │                  │─── 회원 저장/조회 ─────────────────▶│
     │◀── JWT 반환 ─────│                    │                 │
```

## 데이터 흐름

### 가격 예측 요청

```
[Flutter]           [ML Service]              [Model]
    │                    │                       │
    │── POST /predict ──▶│                       │
    │                    │── 데이터 전처리 ─────▶│
    │                    │◀── 예측 결과 ─────────│
    │                    │── 신뢰도 계산         │
    │                    │── 가격 범위 계산      │
    │◀── 예측 응답 ──────│                       │
```

## 배포 환경

| 환경 | ML Service | User Service | Database |
|------|------------|--------------|----------|
| **Development** | localhost:5001 | localhost:8080 | H2 In-Memory |
| **Android Emulator** | 10.0.2.2:5001 | 10.0.2.2:8080 | H2 In-Memory |
| **Production** | TBD | TBD | MySQL |

---

*Last Updated: 2025-11-26*
