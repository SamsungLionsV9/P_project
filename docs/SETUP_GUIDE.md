# 개발 환경 설정 가이드

## 사전 요구사항

| 소프트웨어 | 버전 | 용도 |
|------------|------|------|
| Python | 3.10+ | ML 서비스 |
| Java JDK | 17+ | User 서비스 |
| Flutter SDK | 3.x | 모바일 앱 |
| Android Studio | Latest | 안드로이드 에뮬레이터 |

---

## 1. ML Service 설정

### 1.1 의존성 설치

```bash
cd used-car-price-predictor
pip install -r requirements.txt
```

**주요 패키지**:
- `fastapi` - REST API 프레임워크
- `uvicorn` - ASGI 서버
- `xgboost` - ML 모델
- `pandas` - 데이터 처리

### 1.2 서버 실행

```bash
python run_server.py
```

**확인**:
```bash
curl http://localhost:5001/health
# {"status": "healthy", "version": "1.0.0"}
```

---

## 2. User Service 설정

### 2.1 환경 변수 (선택)

`user-service/src/main/resources/application.yml`

```yaml
spring:
  mail:
    username: ${MAIL_USERNAME:}      # Gmail 주소
    password: ${MAIL_PASSWORD:}      # Gmail 앱 비밀번호
```

> **Note**: 이메일 설정 없이도 동작합니다. 인증 코드는 서버 콘솔에 출력됩니다.

### 2.2 서버 실행

**Windows**:
```powershell
cd user-service
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
.\gradlew bootRun
```

**macOS/Linux**:
```bash
cd user-service
./gradlew bootRun
```

**확인**:
```bash
curl http://localhost:8080/api/auth/health
# {"status": "healthy", "message": "Spring Boot User Management API"}
```

---

## 3. Flutter App 설정

### 3.1 의존성 설치

```bash
cd flutter_app
flutter pub get
```

### 3.2 에뮬레이터 실행

```bash
# 에뮬레이터 목록 확인
flutter emulators

# 에뮬레이터 실행
flutter emulators --launch <emulator_id>
```

### 3.3 앱 실행

```bash
flutter run
```

### 3.4 API URL 설정

앱은 자동으로 환경을 감지합니다:

| 환경 | ML Service | User Service |
|------|------------|--------------|
| Android Emulator | `10.0.2.2:5001` | `10.0.2.2:8080` |
| iOS Simulator | `localhost:5001` | `localhost:8080` |
| Web | `localhost:5001` | `localhost:8080` |

---

## 4. 전체 서비스 실행 순서

```
1. ML Service 시작     → python run_server.py
2. User Service 시작   → ./gradlew bootRun
3. Flutter App 실행    → flutter run
```

---

## 5. 개발 팁

### Hot Reload

Flutter 앱 실행 중 코드 수정 시:
- **r** : Hot Reload (상태 유지)
- **R** : Hot Restart (상태 초기화)

### 서버 로그 확인

**ML Service**:
```bash
# 예측 요청 로그
INFO: POST /predict - 200 OK
```

**User Service**:
```
========================================
🔐 [인증 코드] user@example.com -> 123456
========================================
```

### 데이터베이스 확인 (H2 Console)

개발 환경에서 H2 콘솔에 접속하여 DB를 확인할 수 있습니다:

- **URL**: `http://localhost:8080/h2-console`
- **JDBC URL**: `jdbc:h2:mem:cardb`
- **Username**: `sa`
- **Password**: (비워둠)

---

## 6. 문제 해결

### 포트 충돌

```powershell
# 사용 중인 포트 확인
netstat -ano | findstr :8080

# 프로세스 종료
taskkill /F /PID <PID>
```

### Gradle 빌드 실패

```bash
cd user-service
./gradlew clean build
```

### Flutter 의존성 문제

```bash
flutter clean
flutter pub get
```

---

*Last Updated: 2025-11-26*
