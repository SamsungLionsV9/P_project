#!/bin/bash
# ngrok MySQL 터널 시작 스크립트

echo "=========================================="
echo "🚇 ngrok MySQL 터널 시작"
echo "=========================================="
echo ""

# ngrok 설치 확인
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok이 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "  brew install ngrok"
    echo ""
    echo "또는 https://ngrok.com/download 에서 다운로드"
    exit 1
fi

# ngrok 인증 확인
if [ ! -f ~/.ngrok2/ngrok.yml ] && [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo "⚠️ ngrok 인증이 필요합니다."
    echo ""
    echo "1. https://ngrok.com 에서 무료 계정 생성"
    echo "2. 인증 토큰 받기"
    echo "3. 다음 명령어 실행:"
    echo "   ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    exit 1
fi

echo "✅ ngrok 설정 확인 완료"
echo ""
echo "🔗 MySQL 터널 시작 중..."
echo "📝 아래 URL을 팀원들에게 공유하세요!"
echo ""
echo "=========================================="
echo ""

# ngrok 터널 시작
ngrok tcp 3306

