# 중고차 시세 예측 서비스

> AI 기반 중고차 가격 예측 및 구매 타이밍 분석 플랫폼

## 프로젝트 개요

본 프로젝트는 머신러닝 모델을 활용하여 중고차 시세를 예측하고, 최적의 구매/판매 타이밍을 분석하는 통합 서비스입니다.

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **가격 예측** | XGBoost 모델 기반 중고차 시세 예측 (MAPE 10% 이하) |
| **타이밍 분석** | 계절성, 신차 출시, 시장 동향 기반 구매/판매 타이밍 추천 |
| **유사 차량 검색** | 예측 가격 대비 실제 매물 비교 분석 |
| **사용자 인증** | 이메일 인증 + OAuth2 소셜 로그인 (네이버, 카카오, 구글) |

## 기술 스택

### Backend
- **ML Service**: Python 3.10+, FastAPI, XGBoost, Pandas
- **User Service**: Java 17, Spring Boot 3.x, Spring Security, JPA

### Frontend
- **Mobile App**: Flutter 3.x, Dart

### Database
- **Production**: MySQL 8.0
- **Development**: H2 In-Memory DB

## 문서 목록

| 문서 | 설명 |
|------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 시스템 아키텍처 및 서비스 구조 |
| [API_SPECIFICATION.md](./API_SPECIFICATION.md) | REST API 명세서 |
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | 개발 환경 설정 가이드 |
| [MODEL_SPECIFICATION.md](./MODEL_SPECIFICATION.md) | ML 모델 상세 명세 |

## 빠른 시작

```bash
# 1. ML 서비스 실행
cd used-car-price-predictor
pip install -r requirements.txt
python run_server.py

# 2. User 서비스 실행
cd user-service
./gradlew bootRun

# 3. Flutter 앱 실행
cd flutter_app
flutter pub get
flutter run
```

## 팀 정보

- **Repository**: [SamsungLionsV9/P_project](https://github.com/SamsungLionsV9/P_project)
- **Branch**: `feature/flutter-user-service`

---

*Last Updated: 2025-11-26*
