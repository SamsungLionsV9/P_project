#!/bin/bash

echo "=========================================="
echo "🚀 Flutter 웹 애플리케이션 실행"
echo "=========================================="
echo ""

# 권한 확인 및 수정
if [ ! -w "$HOME/.config" ]; then
    echo "⚠️  권한 문제 감지: ~/.config 디렉토리"
    echo "다음 명령어를 터미널에서 실행하세요:"
    echo "  sudo chown -R \$(whoami) ~/.config"
    echo "  mkdir -p ~/.config/flutter"
    echo ""
    echo "권한 수정 후 이 스크립트를 다시 실행하세요."
    exit 1
fi

# Flutter 설정 디렉토리 생성
mkdir -p ~/.config/flutter 2>/dev/null

if [ ! -d "$HOME/.config/flutter" ]; then
    echo "❌ Flutter 설정 디렉토리 생성 실패"
    echo "다음 명령어를 터미널에서 실행하세요:"
    echo "  sudo chown -R \$(whoami) ~/.config"
    echo "  mkdir -p ~/.config/flutter"
    exit 1
fi

# 프로젝트 디렉토리로 이동
cd "$(dirname "$0")/flutter_app" || exit 1

echo "📦 Flutter 의존성 설치 중..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ 의존성 설치 실패"
    exit 1
fi

echo ""
echo "🌐 Flutter 웹 애플리케이션 실행 중..."
echo "   브라우저가 자동으로 열립니다..."
echo ""

# 웹 브라우저에서 실행
flutter run -d chrome --web-port=8081

