#!/bin/bash

echo "=========================================="
echo "🚀 Flutter 앱 실행 가이드"
echo "=========================================="
echo ""

# 1단계: 에뮬레이터 목록 확인
echo "📱 1단계: 사용 가능한 에뮬레이터 확인"
echo "명령어: flutter emulators"
echo ""
flutter emulators
echo ""

# 2단계: 에뮬레이터 실행
echo "📱 2단계: 에뮬레이터 실행"
echo "명령어: flutter emulators --launch <에뮬레이터_이름>"
echo "또는: emulator -avd <에뮬레이터_이름>"
echo ""
echo "예시:"
echo "  flutter emulators --launch Pixel_5_API_33"
echo "  또는"
echo "  emulator -avd Pixel_5_API_33 &"
echo ""
read -p "에뮬레이터를 실행하셨나요? (Enter를 눌러 계속...)"

# 3단계: 에뮬레이터가 준비될 때까지 대기
echo ""
echo "⏳ 3단계: 에뮬레이터 준비 대기 (약 30초)"
echo "명령어: flutter devices"
echo ""
for i in {1..6}; do
    echo "대기 중... ($i/6)"
    sleep 5
    if flutter devices | grep -q "emulator"; then
        echo "✅ 에뮬레이터 감지됨!"
        break
    fi
done
echo ""

# 4단계: 연결된 디바이스 확인
echo "📱 4단계: 연결된 디바이스 확인"
echo "명령어: flutter devices"
echo ""
flutter devices
echo ""

# 5단계: Flutter 앱 디렉토리로 이동
echo "📂 5단계: Flutter 앱 디렉토리로 이동"
echo "명령어: cd flutter_app"
echo ""
cd flutter_app || exit 1
pwd
echo ""

# 6단계: Flutter 앱 실행
echo "🚀 6단계: Flutter 앱 실행"
echo "명령어: flutter run -d <디바이스_ID>"
echo ""
DEVICE_ID=$(flutter devices | grep "emulator" | head -1 | awk '{print $1}')
if [ -z "$DEVICE_ID" ]; then
    echo "❌ 에뮬레이터를 찾을 수 없습니다."
    echo "수동으로 디바이스 ID를 입력하세요:"
    read -p "디바이스 ID: " DEVICE_ID
fi

echo "디바이스 ID: $DEVICE_ID"
echo ""
echo "Flutter 앱을 실행합니다..."
echo "⏳ 빌드 중... (약 1-2분 소요)"
echo ""
flutter run -d "$DEVICE_ID"
