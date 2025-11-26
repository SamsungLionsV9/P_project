#!/bin/bash

# Spring Boot 회원 관리 API 테스트 스크립트

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Spring Boot 회원 관리 API 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BASE_URL="http://localhost:8080/api/auth"

# 1. 헬스체크
echo "1️⃣ 헬스체크 테스트"
curl -s -X GET "$BASE_URL/health" | python3 -m json.tool
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2. 회원가입
echo "2️⃣ 회원가입 테스트"
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!",
    "phoneNumber": "010-1234-5678"
  }')

echo "$SIGNUP_RESPONSE" | python3 -m json.tool
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. 로그인
echo "3️⃣ 로그인 테스트"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool

# JWT 토큰 추출
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

echo ""
echo "📝 JWT 토큰: ${TOKEN:0:50}..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. 회원 정보 조회
if [ -n "$TOKEN" ]; then
    echo "4️⃣ 회원 정보 조회 테스트"
    curl -s -X GET "$BASE_URL/me" \
      -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 5. 로그아웃
    echo "5️⃣ 로그아웃 테스트"
    curl -s -X POST "$BASE_URL/logout" | python3 -m json.tool
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 6. 회원 탈퇴 (선택)
    read -p "회원 탈퇴 테스트를 진행하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "6️⃣ 회원 탈퇴 테스트"
        curl -s -X DELETE "$BASE_URL/me" \
          -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
else
    echo "❌ 로그인 실패: JWT 토큰을 받지 못했습니다"
fi

echo "✅ API 테스트 완료!"
echo ""

