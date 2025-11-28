#!/bin/bash
# 통합 API 테스트 스크립트

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           Car-Sentix 통합 API 테스트                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 결과 카운터
PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"
    
    if [ "$method" == "POST" ]; then
        response=$(curl -s -X POST -H "Content-Type: application/json" -d "$data" "$url" 2>/dev/null)
    else
        response=$(curl -s "$url" 2>/dev/null)
    fi
    
    if [ -n "$response" ]; then
        echo -e "${GREEN}✓${NC} $name"
        echo "  → $(echo $response | head -c 100)..."
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $name - 연결 실패"
        ((FAIL++))
    fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 1. FastAPI ML 서비스 (8001)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Health Check" "http://localhost:8001/api/health"
test_endpoint "인기 모델 (국산)" "http://localhost:8001/api/popular?category=domestic&limit=3"
test_endpoint "인기 모델 (수입)" "http://localhost:8001/api/popular?category=imported&limit=3"
test_endpoint "추천 차량" "http://localhost:8001/api/recommendations?limit=3"
test_endpoint "가격 예측" "http://localhost:8001/api/predict" "POST" '{"brand":"현대","model":"그랜저 (GN7)","year":2023,"mileage":30000,"fuel":"가솔린"}'
test_endpoint "통합 분석" "http://localhost:8001/api/smart-analysis" "POST" '{"brand":"기아","model":"K5 (DL3)","year":2022,"mileage":40000,"fuel":"가솔린","has_sunroof":true}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏢 2. 관리자 API (8001)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "대시보드 통계" "http://localhost:8001/api/admin/dashboard-stats"
test_endpoint "일별 요청 수" "http://localhost:8001/api/admin/daily-requests?days=7"
test_endpoint "분석 이력" "http://localhost:8001/api/admin/history?limit=5"
test_endpoint "차량 데이터 (국산)" "http://localhost:8001/api/admin/vehicles?category=domestic&limit=3"
test_endpoint "차량 데이터 (수입)" "http://localhost:8001/api/admin/vehicles?category=imported&limit=3"
test_endpoint "차량 통계" "http://localhost:8001/api/admin/vehicle-stats"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 3. Spring Boot 사용자 서비스 (8080)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Spring Boot Health Check
response=$(curl -s "http://localhost:8080/api/auth/health" 2>/dev/null)
if [ -n "$response" ]; then
    echo -e "${GREEN}✓${NC} Health Check"
    ((PASS++))
else
    # 8080 포트 자체가 열려있는지 확인
    nc_result=$(nc -z localhost 8080 2>/dev/null && echo "open" || echo "closed")
    if [ "$nc_result" == "open" ]; then
        echo -e "${YELLOW}△${NC} Spring Boot 실행 중 (health API 없음)"
    else
        echo -e "${RED}✗${NC} Spring Boot 연결 실패 (8080 포트 닫힘)"
        ((FAIL++))
    fi
fi

# 사용자 목록 (인증 필요)
echo -e "${YELLOW}△${NC} 사용자 목록 - 인증 토큰 필요 (테스트 스킵)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚗 4. 옵션 정보 포함 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "차량 데이터에 옵션 필드 포함 확인:"
response=$(curl -s "http://localhost:8001/api/admin/vehicles?category=domestic&limit=1" 2>/dev/null)
if echo "$response" | grep -q "options"; then
    echo -e "${GREEN}✓${NC} 옵션 필드 포함됨"
    echo "  → $(echo $response | python3 -c "import sys,json; d=json.load(sys.stdin); v=d.get('vehicles',[]); print(v[0].get('options','없음') if v else '데이터 없음')" 2>/dev/null)"
    ((PASS++))
else
    echo -e "${RED}✗${NC} 옵션 필드 없음"
    ((FAIL++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 테스트 결과"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}통과: $PASS${NC} / ${RED}실패: $FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}🎉 모든 테스트 통과!${NC}"
else
    echo -e "\n${YELLOW}⚠️  일부 테스트 실패. 서버 상태를 확인하세요.${NC}"
fi

