# 🚀 서버 실행 가이드

중고차 가격 예측 시스템의 모든 서비스를 실행하는 방법을 안내합니다.

## 📋 목차

- [필수 사전 준비](#필수-사전-준비)
- [서비스 구성](#서비스-구성)
- [실행 방법](#실행-방법)
- [서비스 확인](#서비스-확인)
- [문제 해결](#문제-해결)

---

## 필수 사전 준비

### 1. Python 환경 설정

```bash
# Python 3.8 이상 필요
python3 --version

# 필요한 패키지 설치
pip install -r requirements.txt
pip install uvicorn fastapi
```

### 2. Java 환경 설정

```bash
# Java 17 이상 필요
java -version

# Gradle 권한 확인
chmod +x user-service/gradlew
```

### 3. Flutter 환경 설정

```bash
# Flutter 설치 확인
flutter doctor -v

# Flutter 권한 문제 해결 (macOS)
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
```

### 4. MySQL 데이터베이스

```bash
# MySQL 실행 확인
mysql --version

# 데이터베이스 생성 (필요시)
mysql -u root -p
CREATE DATABASE car_database;
```

---

## 서비스 구성

시스템은 3개의 주요 서비스로 구성됩니다:

| 서비스 | 포트 | 기술 스택 | 설명 |
|--------|------|-----------|------|
| **ML Service** | 8001 | Python/FastAPI | 머신러닝 모델 API |
| **User Service** | 8080 | Spring Boot | 사용자 인증 및 관리 |
| **Flutter Web** | - | Flutter Web | 웹 프론트엔드 |

---

## 실행 방법

### 방법 1: 자동 실행 스크립트 (권장) ⭐

```bash
# 프로젝트 루트에서 실행
./start_all_services.sh
```

### 방법 2: 수동 실행

#### 터미널 1 - ML Service (Python/FastAPI)

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8001
```

**실행 확인:**
- 콘솔에 `INFO:     Uvicorn running on http://0.0.0.0:8001` 메시지 표시
- http://localhost:8001/docs 접속 가능

#### 터미널 2 - User Service (Spring Boot)

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main/user-service
./gradlew bootRun
```

**실행 확인:**
- 콘솔에 `Started CarUserManagementApplication` 메시지 표시
- http://localhost:8080/api/auth/health 접속 가능

#### 터미널 3 - Flutter Web App

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main/flutter_app
flutter pub get
flutter run -d chrome
```

**실행 확인:**
- Chrome 브라우저가 자동으로 열림
- Flutter 앱이 표시됨

---

## 서비스 확인

### 1. ML Service 확인

```bash
# 헬스체크
curl http://localhost:8001/health

# API 문서
open http://localhost:8001/docs
```

### 2. User Service 확인

```bash
# 헬스체크
curl http://localhost:8080/api/auth/health

# 응답 예시
# {"status":"healthy","message":"Spring Boot User Management API","version":"1.0.0"}
```

### 3. Flutter Web 확인

- Chrome 브라우저에서 자동으로 열림
- 회원가입/로그인 화면이 표시됨

---

## 문제 해결

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -ti:8001
lsof -ti:8080

# 프로세스 종료
lsof -ti:8001 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

### ML Service 실행 오류

```bash
# Python 경로 확인
which python
which python3

# anaconda 환경 사용 시
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8001
```

### User Service 실행 오류

```bash
# Gradle 권한 확인
chmod +x user-service/gradlew

# Gradle 래퍼 업데이트
cd user-service
./gradlew wrapper --gradle-version=8.5
```

### Flutter 권한 오류

```bash
# macOS 권한 수정
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter

# Flutter Doctor 실행
flutter doctor -v
```

### 데이터베이스 연결 오류

```bash
# MySQL 실행 확인
brew services list | grep mysql

# MySQL 시작
brew services start mysql

# 데이터베이스 연결 테스트
mysql -u root -p -e "USE car_database; SHOW TABLES;"
```

### CORS 오류

- User Service의 `SecurityConfig.java`에서 CORS 설정 확인
- Flutter 앱 포트가 허용 목록에 포함되어 있는지 확인

---

## 서비스 종료

### 모든 서비스 종료

```bash
# ML Service 종료
pkill -f "uvicorn ml-service"

# User Service 종료
pkill -f "gradlew"

# 포트 강제 종료
lsof -ti:8001 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

### 개별 서비스 종료

- **ML Service**: 터미널에서 `Ctrl+C`
- **User Service**: 터미널에서 `Ctrl+C`
- **Flutter Web**: 브라우저 닫기 또는 터미널에서 `Ctrl+C`

---

## 환경 변수 설정

### User Service (application.yml)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/car_database
    username: root
    password: Project1!
  
  mail:
    username: ${MAIL_USERNAME:your-email@gmail.com}
    password: ${MAIL_PASSWORD:your-app-password}
```

### ML Service

환경 변수는 기본값으로 설정되어 있으며, 필요시 수정 가능합니다.

---

## 개발 모드

### ML Service (자동 리로드)

```bash
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8001 --reload
```

### User Service (자동 리로드)

Spring Boot DevTools가 활성화되어 있으면 자동으로 리로드됩니다.

### Flutter Web (Hot Reload)

Flutter는 기본적으로 Hot Reload를 지원합니다.
- `r`: Hot Reload
- `R`: Hot Restart
- `q`: 종료

---

## 프로덕션 배포

프로덕션 환경에서는 다음을 고려하세요:

1. **환경 변수**: 민감한 정보는 환경 변수로 관리
2. **HTTPS**: SSL/TLS 인증서 설정
3. **로드 밸런싱**: 여러 인스턴스 실행
4. **모니터링**: 로그 및 메트릭 수집
5. **백업**: 데이터베이스 정기 백업

---

## 추가 리소스

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Spring Boot 문서](https://spring.io/projects/spring-boot)
- [Flutter 문서](https://flutter.dev/docs)

---

## 문의 및 지원

문제가 발생하면 다음을 확인하세요:

1. 로그 파일 확인
2. 포트 충돌 확인
3. 환경 변수 설정 확인
4. 데이터베이스 연결 확인

---

**마지막 업데이트**: 2025-11-26

