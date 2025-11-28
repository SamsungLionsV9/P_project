# 🚀 MySQL 협업 빠른 설정 가이드

## 📋 방법 1: ngrok 사용 (추천 ⭐)

가장 간단하고 안전한 방법입니다.

### Step 1: ngrok 설치

```bash
brew install ngrok
```

### Step 2: ngrok 계정 생성 및 인증

1. https://ngrok.com 에서 무료 계정 생성
2. 인증 토큰 받기
3. 토큰 설정:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: MySQL 터널 시작

```bash
# 자동 스크립트 사용
./setup/start_ngrok_tunnel.sh

# 또는 직접 실행
ngrok tcp 3306
```

출력 예시:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

### Step 4: 외부 접근용 사용자 생성

```bash
mysql -u root -p car_database < setup/create_remote_user.sql
```

비밀번호 변경 (선택):
```sql
ALTER USER 'team_user'@'%' IDENTIFIED BY '새로운강력한비밀번호';
```

### Step 5: 팀원들에게 정보 공유

다음 정보를 팀원들에게 공유하세요:

- **MySQL 호스트**: `0.tcp.ngrok.io` (ngrok 출력에서 확인)
- **MySQL 포트**: `12345` (ngrok 출력에서 확인)
- **사용자**: `team_user`
- **비밀번호**: (위에서 설정한 비밀번호)
- **데이터베이스**: `car_database`

### Step 6: 팀원이 application.yml 설정

팀원들은 `setup/application.yml.remote.example` 파일을 참고하여 설정:

```yaml
spring:
  datasource:
    url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: team_user
    password: TeamPassword123!@#  # 위에서 설정한 비밀번호
```

---

## 📋 방법 2: 공인 IP 사용

영구적이지만 보안 주의가 필요합니다.

### Step 1: 공인 IP 확인

```bash
curl ifconfig.me
```

### Step 2: MySQL 외부 접근 설정

```bash
# 자동 스크립트 사용
./setup/setup_mysql_remote.sh
# 방법 2 선택

# 또는 수동 설정
# 1. MySQL 설정 파일 수정: /opt/homebrew/etc/my.cnf
# 2. [mysqld] 섹션에 추가: bind-address = 0.0.0.0
# 3. MySQL 재시작: brew services restart mysql
```

### Step 3: 외부 접근용 사용자 생성

```bash
mysql -u root -p car_database < setup/create_remote_user.sql
```

### Step 4: 방화벽 포트 오픈

```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/mysql/bin/mysqld
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/mysql/bin/mysqld
```

### Step 5: 공유기 포트 포워딩 (필요시)

1. 공유기 관리 페이지 접속
2. 포트 포워딩 설정:
   - 외부 포트: 3306
   - 내부 IP: MySQL 서버의 로컬 IP
   - 내부 포트: 3306

### Step 6: 팀원들에게 정보 공유

- **MySQL 호스트**: (공인 IP)
- **MySQL 포트**: 3306
- **사용자**: team_user
- **비밀번호**: (설정한 비밀번호)

---

## ✅ 확인 방법

### 서버 측 (MySQL 호스트)

```bash
# 외부 접근용 사용자 확인
mysql -u root -p -e "SELECT user, host FROM mysql.user WHERE user = 'team_user';"

# bind-address 확인 (공인 IP 사용 시)
mysql -u root -p -e "SHOW VARIABLES LIKE 'bind_address';"
```

### 클라이언트 측 (팀원)

```bash
# MySQL 클라이언트로 접속 테스트
mysql -h 0.tcp.ngrok.io -P 12345 -u team_user -p

# 또는 Spring Boot 실행 테스트
cd user-service
./gradlew bootRun
```

---

## 🆘 문제 해결

### "Access denied" 오류

```sql
-- 권한 재부여
GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%';
FLUSH PRIVILEGES;
```

### "Can't connect to MySQL server" 오류

1. MySQL이 실행 중인지 확인:
   ```bash
   brew services list
   ```

2. ngrok이 실행 중인지 확인:
   ```bash
   # ngrok 웹 인터페이스 확인
   # 브라우저에서 http://127.0.0.1:4040 접속
   ```

3. 방화벽 확인 (공인 IP 사용 시)

### ngrok URL이 변경됨

ngrok 무료 버전은 재시작 시 URL이 변경됩니다. 팀원들에게 새 URL을 공유하세요.

---

## 📝 체크리스트

### 서버 측

- [ ] ngrok 설치 및 인증 완료 (방법 1)
- [ ] 또는 MySQL bind-address 설정 완료 (방법 2)
- [ ] 외부 접근용 사용자 생성 완료
- [ ] ngrok 터널 실행 중 (방법 1)
- [ ] 방화벽 포트 오픈 (방법 2)
- [ ] 팀원들에게 접속 정보 공유

### 클라이언트 측 (팀원)

- [ ] application.yml에 외부 MySQL URL 설정
- [ ] 접속 테스트 완료
- [ ] Spring Boot 서버 실행 성공

---

## 🔐 보안 주의사항

1. **강력한 비밀번호 사용**
2. **개발 환경에서만 사용**
3. **특정 IP만 허용** (가능한 경우)
4. **SSL 연결 사용** (프로덕션)

---

## 📚 상세 가이드

- **상세 설정 가이드**: `setup/MYSQL_REMOTE_ACCESS.md`
- **협업 요약**: `setup/MYSQL_COLLABORATION_SUMMARY.md`

