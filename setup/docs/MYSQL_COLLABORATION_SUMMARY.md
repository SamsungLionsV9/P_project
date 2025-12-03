# 🤝 MySQL 협업 및 CSV Import 요약

## 📌 요약

### 1. MySQL 외부 접근 설정

로컬 MySQL을 팀원들이 다른 네트워크에서 접근할 수 있도록 설정하는 방법:

**추천 방법:**
- **ngrok 사용** (가장 간단하고 안전)
- **공인 IP + 포트 포워딩** (영구적이지만 보안 주의)

자세한 내용: `setup/MYSQL_REMOTE_ACCESS.md`

### 2. CSV 파일을 MySQL에 저장

**단계:**
1. 테이블 생성: `setup/create_csv_tables.sql`
2. Import 실행: `setup/import_csv_to_mysql.py`

자세한 내용: `setup/CSV_IMPORT_GUIDE.md`

---

## 🚀 빠른 시작

### Step 1: MySQL 외부 접근 설정 (ngrok 사용)

```bash
# ngrok 설치
brew install ngrok

# ngrok 계정 생성 후 인증 토큰 설정
ngrok config add-authtoken YOUR_TOKEN

# MySQL 터널 생성
ngrok tcp 3306
```

출력된 URL을 팀원들에게 공유:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

### Step 2: 팀원이 application.yml 수정

```yaml
spring:
  datasource:
    url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: root
    password: YOUR_PASSWORD
```

### Step 3: CSV 테이블 생성

```bash
mysql -u root -p car_database < setup/create_csv_tables.sql
```

### Step 4: CSV Import

```bash
# 환경 변수 설정
export MYSQL_HOST=localhost
export MYSQL_PASSWORD=your_password

# 모든 CSV import
python setup/import_csv_to_mysql.py --all
```

---

## 📊 생성되는 테이블

| 테이블명 | 설명 | CSV 파일 |
|---------|------|----------|
| `domestic_car_details` | 국산차 상세 정보 | `complete_domestic_details.csv` |
| `imported_car_details` | 외제차 상세 정보 | `complete_imported_details.csv` |
| `new_car_schedule` | 신차 출시 일정 | `new_car_schedule.csv` |

---

## 🔐 보안 주의사항

1. **개발 환경에서만 사용**
2. **강력한 비밀번호 설정**
3. **특정 IP만 허용** (가능한 경우)
4. **SSL 연결 사용** (프로덕션)

---

## 📚 상세 가이드

- **MySQL 외부 접근**: `setup/MYSQL_REMOTE_ACCESS.md`
- **CSV Import**: `setup/CSV_IMPORT_GUIDE.md`
- **테이블 스키마**: `setup/create_csv_tables.sql`

---

## ✅ 체크리스트

### 서버 측 (MySQL 호스트)

- [ ] MySQL 외부 접근 설정 완료 (ngrok 또는 공인 IP)
- [ ] 외부 접근용 사용자 생성 및 권한 부여
- [ ] CSV 테이블 생성 완료
- [ ] CSV 데이터 import 완료
- [ ] 팀원들에게 접속 정보 공유

### 클라이언트 측 (팀원)

- [ ] `application.yml`에 외부 MySQL URL 설정
- [ ] Spring Boot 서버 실행 테스트
- [ ] 데이터베이스 연결 확인

---

## 🆘 문제 해결

### MySQL 인증 오류 (MySQL 8.0+)

```sql
-- 사용자 인증 방식 변경
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;
```

### ngrok URL 변경

ngrok 무료 버전은 재시작 시 URL이 변경됩니다. 팀원들에게 새 URL을 공유하세요.

### 포트 포워딩 실패

공유기 설정에서 포트 포워딩이 제대로 되지 않으면, ngrok을 사용하는 것을 권장합니다.

