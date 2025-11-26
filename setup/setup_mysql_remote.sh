#!/bin/bash
# MySQL 외부 접근 설정 스크립트

echo "=========================================="
echo "🌐 MySQL 외부 접근 설정"
echo "=========================================="
echo ""

# MySQL 비밀번호 확인
MYSQL_PASSWORD="${MYSQL_PASSWORD:-Project1!}"
MYSQL_USER="${MYSQL_USER:-root}"

echo "📋 방법 선택:"
echo "1. ngrok 사용 (추천 - 간단하고 안전)"
echo "2. 공인 IP 사용 (영구적이지만 보안 주의)"
echo ""
read -p "선택 (1 또는 2): " choice

case $choice in
    1)
        echo ""
        echo "🔧 ngrok 설정..."
        
        # ngrok 설치 확인
        if ! command -v ngrok &> /dev/null; then
            echo "❌ ngrok이 설치되어 있지 않습니다."
            echo "설치 방법:"
            echo "  brew install ngrok"
            echo "또는 https://ngrok.com/download 에서 다운로드"
            exit 1
        fi
        
        # ngrok 인증 확인
        if [ ! -f ~/.ngrok2/ngrok.yml ] && [ ! -f ~/.config/ngrok/ngrok.yml ]; then
            echo "⚠️ ngrok 인증이 필요합니다."
            echo "1. https://ngrok.com 에서 무료 계정 생성"
            echo "2. 인증 토큰 받기"
            echo "3. 다음 명령어 실행:"
            echo "   ngrok config add-authtoken YOUR_TOKEN"
            exit 1
        fi
        
        echo ""
        echo "✅ ngrok 설정 완료!"
        echo ""
        echo "📝 다음 단계:"
        echo "1. 새 터미널에서 다음 명령어 실행:"
        echo "   ngrok tcp 3306"
        echo ""
        echo "2. 출력된 URL을 확인 (예: tcp://0.tcp.ngrok.io:12345)"
        echo ""
        echo "3. 팀원들에게 다음 정보 공유:"
        echo "   - MySQL 호스트: 0.tcp.ngrok.io"
        echo "   - MySQL 포트: 12345"
        echo "   - 사용자: $MYSQL_USER"
        echo "   - 비밀번호: (공유할 비밀번호)"
        echo ""
        echo "4. application.yml 예시:"
        echo "   url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?..."
        ;;
        
    2)
        echo ""
        echo "🔧 공인 IP 사용 설정..."
        
        # MySQL 설정 파일 찾기
        MYSQL_CNF=""
        for path in /opt/homebrew/etc/my.cnf /etc/my.cnf /etc/mysql/my.cnf ~/.my.cnf; do
            if [ -f "$path" ]; then
                MYSQL_CNF="$path"
                break
            fi
        done
        
        if [ -z "$MYSQL_CNF" ]; then
            echo "⚠️ MySQL 설정 파일을 찾을 수 없습니다."
            echo "수동으로 생성해야 합니다: /opt/homebrew/etc/my.cnf"
            echo ""
            echo "다음 내용 추가:"
            echo "[mysqld]"
            echo "bind-address = 0.0.0.0"
            exit 1
        fi
        
        echo "📝 MySQL 설정 파일: $MYSQL_CNF"
        
        # bind-address 확인
        if grep -q "bind-address" "$MYSQL_CNF"; then
            echo "⚠️ bind-address가 이미 설정되어 있습니다."
            read -p "수정하시겠습니까? (y/n): " modify
            if [ "$modify" != "y" ]; then
                echo "취소되었습니다."
                exit 0
            fi
            # 기존 설정 수정
            sed -i.bak 's/^bind-address.*/bind-address = 0.0.0.0/' "$MYSQL_CNF"
        else
            # 새로 추가
            if ! grep -q "^\[mysqld\]" "$MYSQL_CNF"; then
                echo "" >> "$MYSQL_CNF"
                echo "[mysqld]" >> "$MYSQL_CNF"
            fi
            echo "bind-address = 0.0.0.0" >> "$MYSQL_CNF"
        fi
        
        echo "✅ bind-address 설정 완료!"
        echo ""
        echo "📝 MySQL 재시작 필요:"
        echo "   brew services restart mysql"
        echo "   또는"
        echo "   sudo systemctl restart mysql"
        echo ""
        
        # 외부 접근용 사용자 생성
        echo "🔐 외부 접근용 사용자 생성..."
        read -p "사용자명 (기본: team_user): " team_user
        team_user=${team_user:-team_user}
        read -sp "비밀번호: " team_password
        echo ""
        
        mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" <<EOF 2>/dev/null
CREATE USER IF NOT EXISTS '$team_user'@'%' IDENTIFIED BY '$team_password';
GRANT ALL PRIVILEGES ON car_database.* TO '$team_user'@'%';
FLUSH PRIVILEGES;
SELECT '✅ 외부 접근용 사용자 생성 완료!' AS status;
EOF
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 외부 접근용 사용자 생성 완료!"
            echo ""
            echo "📝 공인 IP 확인:"
            PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip)
            echo "   공인 IP: $PUBLIC_IP"
            echo ""
            echo "📝 팀원들에게 다음 정보 공유:"
            echo "   - MySQL 호스트: $PUBLIC_IP"
            echo "   - MySQL 포트: 3306"
            echo "   - 사용자: $team_user"
            echo "   - 비밀번호: (위에서 입력한 비밀번호)"
            echo ""
            echo "⚠️ 주의:"
            echo "   - 방화벽에서 3306 포트를 열어야 합니다"
            echo "   - 공유기 포트 포워딩 설정이 필요할 수 있습니다"
        else
            echo "❌ 사용자 생성 실패. MySQL에 직접 접속하여 수동으로 생성하세요."
        fi
        ;;
        
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ 설정 완료!"
echo "=========================================="

