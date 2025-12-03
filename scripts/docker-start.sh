#!/bin/bash
# ============================================================
# Docker 기반 서비스 시작 스크립트 (Linux/macOS/Git Bash)
# 
# 사용법:
#   ./scripts/docker-start.sh        # 전체 서비스 시작
#   ./scripts/docker-start.sh ml     # ML 서비스만
#   ./scripts/docker-start.sh build  # 이미지 재빌드 후 시작
# ============================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo -e "${BLUE}🚀 Car-Sentix Docker 시작${NC}"
echo "=================================="

# 환경 파일 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example에서 복사합니다.${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env 파일 생성됨${NC}"
fi

# 인자 처리
case "${1:-all}" in
    "build")
        echo -e "${BLUE}📦 Docker 이미지 빌드 중...${NC}"
        docker-compose build --no-cache
        echo -e "${BLUE}🔄 서비스 시작 중...${NC}"
        docker-compose up -d
        ;;
    "ml")
        echo -e "${BLUE}🤖 ML Service 시작 중...${NC}"
        docker-compose up -d ml-service
        ;;
    "user")
        echo -e "${BLUE}👤 User Service 시작 중...${NC}"
        docker-compose up -d user-service
        ;;
    "admin")
        echo -e "${BLUE}📊 Admin Dashboard 시작 중...${NC}"
        docker-compose up -d admin-dashboard
        ;;
    "all"|*)
        echo -e "${BLUE}🔄 전체 서비스 시작 중...${NC}"
        docker-compose up -d
        ;;
esac

# 상태 확인
echo ""
echo -e "${GREEN}✓ 서비스 상태:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}📌 서비스 URL:${NC}"
echo "   - ML Service:      http://localhost:8000"
echo "   - User Service:    http://localhost:8080"
echo "   - Admin Dashboard: http://localhost:3001"
echo ""
echo -e "${BLUE}📝 로그 확인: docker-compose logs -f [service_name]${NC}"
echo -e "${BLUE}🛑 중지: docker-compose down${NC}"
