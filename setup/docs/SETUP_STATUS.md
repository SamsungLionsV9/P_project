# ✅ MySQL 협업 설정 완료 상태

## 🎉 완료된 작업

### ✅ 1. ngrok 설치
- ngrok이 설치되었습니다
- 인증 토큰 설정 필요 (https://ngrok.com)

### ✅ 2. 외부 접근용 사용자 생성
- **사용자**: `team_user`
- **비밀번호**: `TeamPassword123!@#`
- **권한**: `car_database.*` 전체 권한
- **접근**: 모든 IP 허용 (`%`)

### ✅ 3. CSV 테이블 생성
다음 테이블이 생성되었습니다:
- ✅ `domestic_car_details` (국산차 상세 정보)
- ✅ `imported_car_details` (외제차 상세 정보)
- ✅ `encar_raw_domestic` (엔카 원본 국산차)
- ✅ `encar_imported_data` (엔카 외제차)
- ✅ `new_car_schedule` (신차 출시 일정)

### ✅ 4. CSV 데이터 Import
- ✅ `new_car_schedule`: 10개 행 import 완료
- ⏳ `domestic_car_details`: 대용량 파일 (~119,000행) - 수동 import 필요
- ⏳ `imported_car_details`: 대용량 파일 (~49,000행) - 수동 import 필요

---

## 📋 남은 작업

### 1. ngrok 인증 설정

```bash
# 1. https://ngrok.com 에서 무료 계정 생성
# 2. 인증 토큰 받기
# 3. 토큰 설정
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 2. 대용량 CSV 데이터 Import (선택사항)

```bash
# 환경 변수 설정
export MYSQL_PASSWORD=Project1!

# 국산차 데이터 import (~119,000행, 시간 소요)
python3 setup/import_csv_to_mysql.py --domestic

# 외제차 데이터 import (~49,000행, 시간 소요)
python3 setup/import_csv_to_mysql.py --imported

# 또는 모든 데이터 import
python3 setup/import_csv_to_mysql.py --all
```

**예상 소요 시간**: 5-10분 (데이터 크기에 따라 다름)

### 3. ngrok 터널 시작

**새 터미널 창**에서 실행:

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main
./setup/start_ngrok_tunnel.sh
```

또는:

```bash
ngrok tcp 3306
```

**⚠️ 중요:** 이 터미널은 계속 실행 상태로 유지해야 합니다!

출력 예시:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

### 4. 팀원들에게 정보 공유

다음 정보를 팀원들에게 공유하세요:

```
MySQL 호스트: 0.tcp.ngrok.io (ngrok 출력에서 확인)
MySQL 포트: 12345 (ngrok 출력에서 확인)
데이터베이스: car_database
사용자: team_user
비밀번호: TeamPassword123!@#
```

### 5. 팀원 설정 가이드

팀원들은 `setup/application.yml.remote.example` 파일을 참고하여 설정:

```yaml
spring:
  datasource:
    url: jdbc:mysql://0.tcp.ngrok.io:12345/car_database?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8&allowPublicKeyRetrieval=true
    username: team_user
    password: TeamPassword123!@#
```

---

## 🔍 확인 명령어

### 사용자 확인
```bash
python3 setup/setup_collaboration.py
```

### 데이터 확인
```bash
python3 -c "
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='Project1!', database='car_database')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM new_car_schedule')
print(f'신차 일정: {cursor.fetchone()[0]}개')
cursor.execute('SELECT COUNT(*) FROM domestic_car_details')
print(f'국산차: {cursor.fetchone()[0]}개')
cursor.execute('SELECT COUNT(*) FROM imported_car_details')
print(f'외제차: {cursor.fetchone()[0]}개')
conn.close()
"
```

---

## 📚 관련 문서

- **완전 설정 가이드**: `setup/COMPLETE_SETUP.md`
- **빠른 설정**: `setup/QUICK_REMOTE_SETUP.md`
- **상세 가이드**: `setup/MYSQL_REMOTE_ACCESS.md`
- **CSV Import**: `setup/CSV_IMPORT_GUIDE.md`

---

## 🆘 문제 해결

### ngrok 인증 오류
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### 사용자 권한 오류
```bash
python3 setup/setup_collaboration.py
# 또는
mysql -u root -p < setup/create_remote_user.sql
```

### CSV Import 오류
```bash
# 패키지 확인
pip install pymysql tqdm pandas

# 다시 import
python3 setup/import_csv_to_mysql.py --all
```

---

## ✅ 체크리스트

- [x] ngrok 설치
- [ ] ngrok 인증 설정
- [x] 외부 접근용 사용자 생성
- [x] CSV 테이블 생성
- [x] 신차 일정 데이터 import
- [ ] 국산차 데이터 import (선택)
- [ ] 외제차 데이터 import (선택)
- [ ] ngrok 터널 시작
- [ ] 팀원들에게 정보 공유

