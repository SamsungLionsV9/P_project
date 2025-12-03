#!/bin/bash
# ============================================================
# Post-create script for Dev Container
# 컨테이너 생성 후 자동으로 실행됨
# ============================================================

set -e

echo "🚀 Car-Sentix 개발 환경 초기화 중..."

# 1. Python 의존성 설치
echo "📦 Python 패키지 설치 중..."
pip install --user -r /workspace/requirements.txt 2>/dev/null || true

# 2. Node.js 의존성 설치 (admin-dashboard)
echo "📦 Node.js 패키지 설치 중..."
if [ -d "/workspace/admin-dashboard" ]; then
    cd /workspace/admin-dashboard
    npm install 2>/dev/null || true
fi

# 3. 환경 변수 파일 생성 (없는 경우)
if [ ! -f "/workspace/.env" ] && [ -f "/workspace/.env.example" ]; then
    echo "📝 .env 파일 생성 중..."
    cp /workspace/.env.example /workspace/.env
fi

# 4. 데이터 디렉토리 확인
echo "📁 디렉토리 구조 확인 중..."
mkdir -p /workspace/data /workspace/logs /workspace/models

# 5. Git hooks 설정 (있는 경우)
if [ -d "/workspace/.git" ]; then
    echo "🔧 Git hooks 설정 중..."
    git config --local core.autocrlf input
fi

# 6. 권한 설정
chmod +x /workspace/scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ 개발 환경 초기화 완료!"
echo ""
echo "📌 서비스 시작 방법:"
echo "   전체 서비스: docker-compose up -d"
echo "   ML 서비스만: docker-compose up ml-service"
echo ""
echo "📌 포트 정보:"
echo "   - ML Service:      http://localhost:8000"
echo "   - User Service:    http://localhost:8080"
echo "   - Admin Dashboard: http://localhost:3001"
echo ""
