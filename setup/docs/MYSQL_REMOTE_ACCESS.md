# 🌐 MySQL 외부 접근 설정 가이드

로컬 MySQL을 팀원들이 다른 네트워크에서도 접근할 수 있도록 설정하는 방법입니다.

## ⚠️ 보안 주의사항

- **개발 환경에서만 사용하세요!**
- 프로덕션 환경에서는 반드시 방화벽과 VPN을 사용하세요.
- 강력한 비밀번호를 설정하세요.

---

## 📋 방법 1: 공인 IP 사용 (같은 인터넷 연결)

### 1-1. 공인 IP 확인

```bash
# 공인 IP 확인
curl ifconfig.me
# 또는
curl ipinfo.io/ip
```

### 1-2. MySQL 외부 접근 허용 설정

#### macOS/Linux

```bash
# MySQL 설정 파일 찾기
mysql --help | grep "Default options" -A 1

# 일반적인 위치:
# macOS: /usr/local/mysql/my.cnf 또는 /etc/my.cnf
# Linux: /etc/mysql/my.cnf 또는 /etc/my.cnf
```

**my.cnf 파일 수정:**

```ini
[mysqld]
bind-address = 0.0.0.0  # 모든 IP에서 접근 허용
# 또는
# bind-address = YOUR_PUBLIC_IP  # 특정 IP만 허용
```

#### Windows

`C:\ProgramData\MySQL\MySQL Server 8.0\my.ini` 파일 수정:

```ini
[mysqld]
bind-address = 0.0.0.0
```

### 1-3. MySQL 재시작

```bash
# macOS (Homebrew)
brew services restart mysql

# Linux
sudo systemctl restart mysql

# Windows
# 서비스 관리자에서 MySQL 재시작
```

### 1-4. 외부 접근 권한 부여

```sql
-- MySQL 접속
mysql -u root -p

-- 외부 접근용 사용자 생성 (모든 IP 허용)
CREATE USER 'team_user'@'%' IDENTIFIED BY '강력한비밀번호123!';

-- 권한 부여
GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%';

-- 특정 IP만 허용하려면
-- CREATE USER 'team_user'@'123.456.789.0' IDENTIFIED BY '비밀번호';
-- GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'123.456.789.0';

FLUSH PRIVILEGES;
```

### 1-5. 방화벽 포트 오픈

#### macOS

```bash
# 방화벽 설정 확인
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# MySQL 포트(3306) 허용
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/mysql/bin/mysqld
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/mysql/bin/mysqld
```

#### Linux (ufw)

```bash
sudo ufw allow 3306/tcp
sudo ufw reload
```

#### Windows

1. 제어판 → Windows Defender 방화벽
2. 고급 설정 → 인바운드 규칙 → 새 규칙
3. 포트 선택 → TCP → 3306 → 연결 허용

### 1-6. 라우터 포트 포워딩 (공유기 사용 시)

1. 공유기 관리 페이지 접속 (보통 `192.168.0.1` 또는 `192.168.1.1`)
2. 포트 포워딩 설정:
   - 외부 포트: 3306
   - 내부 IP: MySQL 서버의 로컬 IP (예: `192.168.0.100`)
   - 내부 포트: 3306
   - 프로토콜: TCP

### 1-7. application.yml 수정

팀원들이 사용할 설정:

```yaml
spring:
  datasource:
    url: jdbc:mysql://YOUR_PUBLIC_IP:3306/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: team_user
    password: 강력한비밀번호123!
```

---

## 📋 방법 2: ngrok 사용 (추천 - 보안성 높음)

ngrok은 안전한 터널을 만들어주는 서비스입니다.

### 2-1. ngrok 설치

```bash
# macOS
brew install ngrok

# 또는 다운로드
# https://ngrok.com/download
```

### 2-2. ngrok 계정 생성 및 인증

1. https://ngrok.com 에서 무료 계정 생성
2. 인증 토큰 받기
3. 토큰 설정:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 2-3. MySQL 터널 생성

```bash
# MySQL 포트(3306) 터널링
ngrok tcp 3306
```

출력 예시:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

### 2-4. application.yml 수정

팀원들이 사용할 설정:

```yaml
spring:
  datasource:
    url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: root  # 또는 team_user
    password: YOUR_PASSWORD
```

**⚠️ 주의:** ngrok 무료 버전은 재시작할 때마다 URL이 변경됩니다. 팀원들에게 새 URL을 공유해야 합니다.

---

## 📋 방법 3: Cloudflare Tunnel (무료, 영구 URL)

Cloudflare Tunnel은 무료로 영구 URL을 제공합니다.

### 3-1. Cloudflared 설치

```bash
# macOS
brew install cloudflared

# 또는 다운로드
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### 3-2. 터널 생성

```bash
# 로그인
cloudflared tunnel login

# 터널 생성
cloudflared tunnel create car-mysql

# 터널 실행
cloudflared tunnel --url tcp://localhost:3306
```

### 3-3. 설정 파일 생성

`~/.cloudflared/config.yml`:

```yaml
tunnel: car-mysql
credentials-file: /Users/YOUR_USERNAME/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: car-mysql.YOUR_DOMAIN.com
    service: tcp://localhost:3306
```

---

## 🧪 접속 테스트

### 팀원이 접속 테스트

```bash
# MySQL 클라이언트로 접속
mysql -h YOUR_PUBLIC_IP -u team_user -p

# 또는 ngrok 사용 시
mysql -h 0.tcp.ngrok.io -P 12345 -u root -p
```

### Spring Boot에서 테스트

```bash
cd user-service
./gradlew bootRun
```

---

## 🔒 보안 강화 팁

1. **강력한 비밀번호 사용**
   ```sql
   ALTER USER 'team_user'@'%' IDENTIFIED BY '복잡한비밀번호123!@#';
   ```

2. **특정 IP만 허용**
   ```sql
   CREATE USER 'team_user'@'123.456.789.0' IDENTIFIED BY '비밀번호';
   ```

3. **읽기 전용 권한만 부여** (필요시)
   ```sql
   GRANT SELECT ON car_database.* TO 'readonly_user'@'%';
   ```

4. **SSL 연결 사용** (프로덕션)
   ```yaml
   url: jdbc:mysql://...?useSSL=true&requireSSL=true
   ```

---

## 📝 체크리스트

- [ ] MySQL `bind-address` 설정 완료
- [ ] 외부 접근용 사용자 생성 및 권한 부여
- [ ] 방화벽 포트 오픈 (또는 ngrok/Cloudflare Tunnel 설정)
- [ ] 공유기 포트 포워딩 (공인 IP 사용 시)
- [ ] 팀원들에게 접속 정보 공유
- [ ] 접속 테스트 완료

---

## 🆘 문제 해결

### "Access denied" 오류

```sql
-- 사용자 권한 확인
SELECT user, host FROM mysql.user;

-- 권한 재부여
GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%';
FLUSH PRIVILEGES;
```

### "Can't connect to MySQL server" 오류

1. MySQL이 실행 중인지 확인:
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status mysql
   ```

2. 포트가 열려있는지 확인:
   ```bash
   # 서버에서
   netstat -an | grep 3306
   
   # 클라이언트에서
   telnet YOUR_IP 3306
   ```

3. 방화벽 확인:
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
   ```

---

## 📚 참고 자료

- [MySQL 공식 문서 - 외부 접근](https://dev.mysql.com/doc/refman/8.0/en/server-options.html#option_mysqld_bind-address)
- [ngrok 문서](https://ngrok.com/docs)
- [Cloudflare Tunnel 문서](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

