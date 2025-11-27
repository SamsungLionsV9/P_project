#!/bin/bash

# 모든 서비스 실행 스크립트

echo "=========================================="
echo "🚀 중고차 가격 예측 시스템 시작"
echo "=========================================="
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")"

# Flutter 권한 확인
if [ ! -d "$HOME/.config/flutter" ]; then
    echo "⚠️  Flutter 권한 문제가 있습니다."
    echo "다음 명령어를 실행하세요:"
    echo "  sudo chown -R \$(whoami) ~/.config"
    echo "  mkdir -p ~/.config/flutter"
    echo ""
    read -p "권한 문제를 해결하셨나요? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "권한 문제를 해결한 후 다시 실행하세요."
        exit 1
    fi
fi

# ML Service 시작
echo "1️⃣ ML Service 시작 중... (포트 8000)"
python3 -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000 --reload &
ML_PID=$!
echo "   PID: $ML_PID"
sleep 3

# ML Service 확인
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ ML Service 실행 중"
else
    echo "   ⚠️  ML Service 시작 실패 (확인 중...)"
fi
echo ""

# User Service 시작
echo "2️⃣ User Service 시작 중... (포트 8080)"
cd user-service
./gradlew bootRun &
USER_PID=$!
echo "   PID: $USER_PID"
cd ..
sleep 8

# User Service 확인
if curl -s http://localhost:8080/api/auth/health > /dev/null; then
    echo "   ✅ User Service 실행 중"
else
    echo "   ⚠️  User Service 시작 중... (약 30초 소요)"
fi
echo ""

# Flutter 앱 시작
echo "3️⃣ Flutter 앱 시작 중..."
cd flutter_app
flutter pub get
if [ $? -eq 0 ]; then
    echo "   ✅ 의존성 설치 완료"
    echo "   🌐 웹 브라우저에서 실행합니다..."
    flutter run -d chrome
else
    echo "   ❌ 의존성 설치 실패"
    echo "   Flutter 권한 문제를 확인하세요."
fi

echo ""
echo "=========================================="
echo "서비스 종료: Ctrl+C 또는 다음 명령어"
echo "  kill $ML_PID $USER_PID"
echo "=========================================="

