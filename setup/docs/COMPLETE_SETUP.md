# 🚀 MySQL 협업 완전 설정 가이드

이 가이드를 따라하시면 MySQL 협업 설정이 완료됩니다.

---

## 📋 사전 준비

1. MySQL이 실행 중인지 확인:
   ```bash
   brew services list | grep mysql
   ```

2. 필요한 패키지 설치:
   ```bash
   pip install pymysql tqdm
   ```

---

## 🔧 Step 1: 외부 접근용 사용자 생성

### 방법 A: Python 스크립트 사용 (추천)

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
python3 setup/setup_collaboration.py
```

스크립트가 다음을 자동으로 수행합니다:
- 외부 접근용 사용자 생성
- CSV 테이블 생성
- 데이터 확인

### 방법 B: SQL 직접 실행

```bash
mysql -u root -p car_database < setup/create_remote_user.sql
```

비밀번호 변경 (선택):
```sql
mysql -u root -p
ALTER USER 'team_user'@'%' IDENTIFIED BY '새로운강력한비밀번호';
FLUSH PRIVILEGES;
```

---

## 📊 Step 2: CSV 테이블 생성

```bash
mysql -u root -p car_database < setup/create_csv_tables.sql
```

또는 Python 스크립트에서 자동으로 생성됩니다.

---

## 📥 Step 3: CSV 데이터 Import

```bash
# 환경 변수 설정
export MYSQL_PASSWORD=Project1!

# 모든 CSV import
python3 setup/import_csv_to_mysql.py --all
```

---

## 🌐 Step 4: ngrok 설정 및 터널 시작

### 4-1. ngrok 계정 생성 및 인증

1. https://ngrok.com 에서 무료 계정 생성
2. 인증 토큰 받기
3. 토큰 설정:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 4-2. MySQL 터널 시작

**새 터미널 창**에서 실행:

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
./setup/start_ngrok_tunnel.sh
```

또는 직접 실행:

```bash
ngrok tcp 3306
```

출력 예시:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

**⚠️ 중요:** 이 터미널은 계속 실행 상태로 유지해야 합니다!

---

## 📝 Step 5: 팀원들에게 정보 공유

다음 정보를 팀원들에게 공유하세요:

### 필수 정보

1. **MySQL 호스트**: `0.tcp.ngrok.io` (ngrok 출력에서 확인)
2. **MySQL 포트**: `12345` (ngrok 출력에서 확인)
3. **데이터베이스**: `car_database`
4. **사용자**: `team_user`
5. **비밀번호**: (Step 1에서 설정한 비밀번호)

### application.yml 설정 예시

팀원들이 `user-service/src/main/resources/application.yml`에 설정:

```yaml
spring:
  datasource:
    url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: team_user
    password: TeamPassword123!@#  # 위에서 설정한 비밀번호
```

또는 `setup/application.yml.remote.example` 파일을 참고하세요.

---

## ✅ 확인 방법

### 서버 측 (MySQL 호스트)

```bash
# 외부 접근용 사용자 확인
mysql -u root -p -e "SELECT user, host FROM mysql.user WHERE user = 'team_user';"

# CSV 테이블 확인
mysql -u root -p car_database -e "SHOW TABLES;"

# CSV 데이터 확인
mysql -u root -p car_database -e "
SELECT 
    'domestic_car_details' AS table_name,
    COUNT(*) AS row_count 
FROM domestic_car_details
UNION ALL
SELECT 
    'imported_car_details' AS table_name,
    COUNT(*) AS row_count 
FROM imported_car_details
UNION ALL
SELECT 
    'new_car_schedule' AS table_name,
    COUNT(*) AS row_count 
FROM new_car_schedule;
"
```

### 클라이언트 측 (팀원)

```bash
# MySQL 클라이언트로 접속 테스트
mysql -h 0.tcp.ngrok.io -P 12345 -u team_user -p

# Spring Boot 실행 테스트
cd user-service
./gradlew bootRun
```

---

## 🔄 ngrok URL 변경 시

ngrok 무료 버전은 재시작할 때마다 URL이 변경됩니다.

1. 새 URL 확인: `ngrok tcp 3306` 실행 후 출력 확인
2. 팀원들에게 새 URL 공유
3. 팀원들이 `application.yml`의 URL 업데이트

---

## 🆘 문제 해결

### "Access denied" 오류

```sql
mysql -u root -p
GRANT ALL PRIVILEGES ON car_database.* TO 'team_user'@'%';
FLUSH PRIVILEGES;
```

### "Can't connect to MySQL server" 오류

1. ngrok이 실행 중인지 확인
2. ngrok 웹 인터페이스 확인: http://127.0.0.1:4040
3. MySQL이 실행 중인지 확인: `brew services list`

### CSV 데이터가 없음

```bash
# CSV import 다시 실행
python3 setup/import_csv_to_mysql.py --all
```

---

## 📋 체크리스트

### 서버 측

- [ ] ngrok 설치 완료
- [ ] ngrok 인증 완료
- [ ] 외부 접근용 사용자 생성 완료
- [ ] CSV 테이블 생성 완료
- [ ] CSV 데이터 import 완료
- [ ] ngrok 터널 실행 중
- [ ] 팀원들에게 접속 정보 공유

### 클라이언트 측 (팀원)

- [ ] application.yml에 외부 MySQL URL 설정
- [ ] 접속 테스트 완료
- [ ] Spring Boot 서버 실행 성공

---

## 📚 관련 문서

- **빠른 설정**: `setup/QUICK_REMOTE_SETUP.md`
- **상세 가이드**: `setup/MYSQL_REMOTE_ACCESS.md`
- **CSV Import**: `setup/CSV_IMPORT_GUIDE.md`

