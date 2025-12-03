# 🚀 빠른 시작 가이드

## ⚠️ 필수: Flutter 권한 문제 해결

터미널에서 다음 명령어를 실행하세요:

```bash
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
```

비밀번호를 입력하면 권한이 수정됩니다.

## 📋 실행 순서

### 방법 1: 자동 실행 스크립트 (권장)

```bash
# 1. 권한 문제 해결
./fix_flutter_permissions.sh

# 2. 모든 서비스 실행
./start_all_services.sh
```

### 방법 2: 수동 실행 (3개 터미널 필요)

#### 터미널 1 - ML Service
```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
python3 -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000
```

#### 터미널 2 - User Service
```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main/user-service
./gradlew bootRun
```

#### 터미널 3 - Flutter 앱
```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main/flutter_app
flutter pub get
flutter run -d chrome
```

## ✅ 서비스 확인

- ML Service: http://localhost:8000/docs
- User Service: http://localhost:8080/api/auth/health
- Flutter 앱: 자동으로 브라우저에서 열림

## 🐛 문제 해결

### Flutter 권한 오류
```bash
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
```

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 종료
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

### Flutter Doctor 실행
```bash
flutter doctor -v
```
