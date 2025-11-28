# Flutter 설치 가이드

## 문제: Flutter 설정 디렉토리 권한 오류

Flutter가 `~/.config/flutter` 디렉토리를 생성할 수 없는 경우 해결 방법입니다.

## 해결 방법

### 방법 1: 수동으로 디렉토리 생성 (권장)

터미널에서 다음 명령어를 실행하세요:

```bash
mkdir -p ~/.config/flutter
chmod 755 ~/.config
chmod 755 ~/.config/flutter
```

### 방법 2: sudo 권한 사용

만약 권한 문제가 계속되면:

```bash
sudo mkdir -p ~/.config/flutter
sudo chown -R $(whoami) ~/.config/flutter
```

### 방법 3: 환경 변수 설정

`~/.zshrc` 또는 `~/.bash_profile`에 다음을 추가:

```bash
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
export PUB_HOSTED_URL=https://pub.flutter-io.cn
```

그리고:
```bash
source ~/.zshrc  # 또는 source ~/.bash_profile
```

## 설치 확인

설정 후 다음 명령어로 확인:

```bash
flutter --version
flutter doctor
```

## Flutter 앱 실행

프로젝트의 Flutter 앱을 실행하려면:

```bash
cd flutter_app
flutter pub get
flutter run
```

## 추가 정보

- Flutter 공식 문서: https://docs.flutter.dev/get-started/install/macos
- 문제가 계속되면 Flutter GitHub Issues를 확인하세요
