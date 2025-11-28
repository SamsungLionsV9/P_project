# 📊 CSV 파일을 MySQL에 Import하는 가이드

CSV 데이터를 MySQL 데이터베이스에 저장하는 방법입니다.

---

## 📋 사전 준비

### 1. 필요한 패키지 설치

```bash
pip install pymysql pandas tqdm
```

또는 프로젝트 루트의 `requirements.txt`에 추가:

```txt
pymysql>=1.1.0
pandas>=2.0.0
tqdm>=4.66.0
```

### 2. MySQL 테이블 생성

```bash
# MySQL 접속
mysql -u root -p

# 테이블 생성
source setup/create_csv_tables.sql;
```

또는 직접 실행:

```bash
mysql -u root -p car_database < setup/create_csv_tables.sql
```

---

## 🚀 Import 실행

### 방법 1: 환경 변수 설정 후 실행

```bash
# 환경 변수 설정
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=car_database

# 모든 CSV 파일 import
python setup/import_csv_to_mysql.py --all
```

### 방법 2: 특정 파일만 import

```bash
# 국산차 상세 정보만
python setup/import_csv_to_mysql.py --domestic

# 외제차 상세 정보만
python setup/import_csv_to_mysql.py --imported

# 신차 출시 일정만
python setup/import_csv_to_mysql.py --schedule
```

### 방법 3: 배치 크기 조정

대용량 파일의 경우 배치 크기를 조정할 수 있습니다:

```bash
python setup/import_csv_to_mysql.py --all --batch-size 5000
```

---

## 📁 Import되는 파일

| 파일명 | 테이블명 | 행 수 (예상) |
|--------|----------|-------------|
| `complete_domestic_details.csv` | `domestic_car_details` | ~119,000 |
| `complete_imported_details.csv` | `imported_car_details` | ~49,000 |
| `new_car_schedule.csv` | `new_car_schedule` | ~10 |

---

## 🔍 Import 확인

### MySQL에서 확인

```sql
-- 테이블별 행 수 확인
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

-- 샘플 데이터 확인
SELECT * FROM domestic_car_details LIMIT 5;
SELECT * FROM new_car_schedule;
```

### Python에서 확인

```python
import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='car_database',
    charset='utf8mb4'
)

cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM domestic_car_details")
print(f"국산차 데이터: {cursor.fetchone()[0]:,}개 행")

cursor.execute("SELECT COUNT(*) FROM imported_car_details")
print(f"외제차 데이터: {cursor.fetchone()[0]:,}개 행")

cursor.close()
connection.close()
```

---

## ⚙️ 설정 옵션

### 환경 변수

스크립트는 다음 환경 변수를 사용합니다:

- `MYSQL_HOST`: MySQL 호스트 (기본: localhost)
- `MYSQL_PORT`: MySQL 포트 (기본: 3306)
- `MYSQL_USER`: MySQL 사용자 (기본: root)
- `MYSQL_PASSWORD`: MySQL 비밀번호 (기본: Project1!)
- `MYSQL_DATABASE`: 데이터베이스명 (기본: car_database)

### 커맨드 라인 옵션

```bash
python setup/import_csv_to_mysql.py --help
```

옵션:
- `--all`: 모든 CSV 파일 import
- `--domestic`: 국산차 상세 정보만
- `--imported`: 외제차 상세 정보만
- `--schedule`: 신차 출시 일정만
- `--batch-size N`: 배치 크기 (기본: 1000)

---

## 🐛 문제 해결

### "ModuleNotFoundError: No module named 'pymysql'"

```bash
pip install pymysql pandas tqdm
```

### "Access denied for user"

MySQL 사용자 권한 확인:

```sql
-- 사용자 확인
SELECT user, host FROM mysql.user;

-- 권한 부여
GRANT ALL PRIVILEGES ON car_database.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### "Table doesn't exist"

테이블 생성 스크립트 실행:

```bash
mysql -u root -p car_database < setup/create_csv_tables.sql
```

### "Duplicate entry" 오류

중복된 `car_id`가 있는 경우, 스크립트는 자동으로 업데이트합니다.
기존 데이터를 유지하려면 테이블의 `UNIQUE KEY` 제약을 제거하세요.

### 메모리 부족

배치 크기를 줄이세요:

```bash
python setup/import_csv_to_mysql.py --all --batch-size 500
```

---

## 📊 성능 최적화

### 대용량 파일 처리

1. **배치 크기 조정**: 메모리에 따라 500~5000 권장
2. **인덱스 일시 제거**: import 후 인덱스 재생성
3. **트랜잭션 크기 조정**: 배치마다 commit

### 인덱스 최적화

```sql
-- Import 전 인덱스 제거 (선택사항)
ALTER TABLE domestic_car_details DROP INDEX idx_car_id;

-- Import 후 인덱스 재생성
ALTER TABLE domestic_car_details ADD INDEX idx_car_id (car_id);
```

---

## ✅ 체크리스트

- [ ] 필요한 패키지 설치 완료 (`pymysql`, `pandas`, `tqdm`)
- [ ] MySQL 테이블 생성 완료 (`create_csv_tables.sql` 실행)
- [ ] 환경 변수 설정 (또는 스크립트 내 기본값 사용)
- [ ] CSV 파일 위치 확인 (`data/` 디렉토리)
- [ ] Import 실행
- [ ] 데이터 확인 (행 수, 샘플 데이터)

---

## 📚 참고 자료

- [pymysql 문서](https://pymysql.readthedocs.io/)
- [pandas 문서](https://pandas.pydata.org/docs/)
- [MySQL LOAD DATA 문서](https://dev.mysql.com/doc/refman/8.0/en/load-data.html)

