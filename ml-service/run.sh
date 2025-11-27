#!/bin/bash

# 중고차 가격 예측 API 서버 실행 스크립트

echo "=================================================="
echo "🚗 중고차 가격 예측 API 서버 시작"
echo "=================================================="
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 프로젝트 루트: $PROJECT_ROOT"
echo "📁 백엔드 디렉토리: $SCRIPT_DIR"
echo ""

# Python 버전 확인
echo "🐍 Python 버전:"
python --version
echo ""

# 의존성 설치 확인
if [ ! -d "venv" ]; then
    echo "⚠️  가상환경이 없습니다."
    echo "다음 명령어로 가상환경을 만들고 의존성을 설치하세요:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
fi

# 환경변수 확인
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✅ .env 파일 발견"
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
else
    echo "⚠️  .env 파일이 없습니다. Groq AI 기능이 제한될 수 있습니다."
fi
echo ""

# 서버 실행
echo "🚀 서버를 시작합니다..."
echo "📡 API 문서: http://localhost:8000/docs"
echo "📡 ReDoc: http://localhost:8000/redoc"
echo ""
echo "=================================================="
echo ""

# 프로젝트 루트로 이동
cd "$PROJECT_ROOT"

# uvicorn 실행
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000 --reload

