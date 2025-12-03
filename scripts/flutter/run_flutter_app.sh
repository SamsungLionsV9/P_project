#!/bin/bash

# Flutter 앱 실행 스크립트

echo "=========================================="
echo "🚀 Flutter 앱 실행 준비"
echo "=========================================="
echo ""

# 권한 확인
if [ ! -d "$HOME/.config/flutter" ]; then
    echo "⚠️  Flutter 설정 디렉토리가 없습니다."
    echo "다음 명령어를 실행하세요:"
    echo "  sudo chown -R \$(whoami) ~/.config"
    echo "  mkdir -p ~/.config/flutter"
    echo ""
    exit 1
fi

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")/flutter_app"

echo "📦 의존성 설치 중..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ 의존성 설치 실패"
    exit 1
fi

echo ""
echo "🔍 사용 가능한 디바이스 확인 중..."
flutter devices

echo ""
echo "🌐 웹 브라우저에서 실행합니다..."
echo "   (다른 디바이스에서 실행하려면: flutter run -d <device-id>)"
echo ""

# 웹 브라우저에서 실행
flutter run -d chrome

