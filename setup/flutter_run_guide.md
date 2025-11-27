# Flutter 앱 실행 가이드

## ⚠️ 권한 문제 해결 필요

Flutter를 실행하기 전에 다음 명령어를 터미널에서 실행하세요:

```bash
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
```

## Flutter 앱 실행 방법

### 1. 의존성 설치

```bash
cd flutter_app
flutter pub get
```

### 2. 실행 가능한 디바이스 확인

```bash
flutter devices
```

### 3. 웹 브라우저에서 실행 (가장 간단)

```bash
flutter run -d chrome
```

또는

```bash
flutter run -d web-server
```

### 4. iOS 시뮬레이터에서 실행 (macOS)

```bash
open -a Simulator
flutter run
```

### 5. Android 에뮬레이터에서 실행

```bash
flutter emulators --launch <emulator_id>
flutter run
```

## 백엔드 서버 실행

Flutter 앱이 백엔드 API를 호출하므로, 먼저 백엔드 서버를 실행해야 합니다:

### ML Service (포트 8000)
```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000
```

### User Service (포트 8080)
```bash
cd user-service
./gradlew bootRun
```

## 문제 해결

### 권한 오류가 계속되면

환경 변수를 설정하여 다른 위치에 설정을 저장:

```bash
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
export PUB_HOSTED_URL=https://pub.flutter-io.cn
```

### Flutter Doctor 실행

설정 확인:
```bash
flutter doctor -v
```

필요한 도구 설치 안내를 따르세요.
