# 🚀 Spring Boot User Service 설정 가이드

이 가이드는 협업자들이 로컬 환경에서 프로젝트를 설정하는 방법을 설명합니다.

## 📋 사전 요구사항

- **Java 17 이상** (JDK 17 또는 23 권장)
- **MySQL 8.0 이상**
- **Gradle** (프로젝트에 포함된 Gradle Wrapper 사용 가능)

## 🔧 설정 단계

### 1. MySQL 데이터베이스 설정

#### MySQL 접속
```bash
mysql -u root -p
```

#### 데이터베이스 및 사용자 생성
```sql
-- setup_mysql.sql 파일 실행
source user-service/setup_mysql.sql;
```

또는 수동으로:
```sql
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS car_database
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 및 권한 부여
CREATE USER IF NOT EXISTS 'car_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON car_database.* TO 'car_user'@'localhost';
FLUSH PRIVILEGES;

-- 데이터베이스 선택
USE car_database;
```

테이블은 Spring Boot가 자동으로 생성합니다 (JPA의 `ddl-auto: update` 설정).

### 2. Application 설정 파일 생성

#### `application.yml` 파일 생성
```bash
cd user-service/src/main/resources
cp application.yml.example application.yml
```

#### `application.yml` 수정
파일을 열어 다음 값들을 설정하세요:

```yaml
spring:
  datasource:
    username: root  # 또는 car_user
    password: YOUR_MYSQL_PASSWORD  # MySQL 비밀번호 입력
    
  security:
    jwt:
      secret: YOUR_JWT_SECRET_KEY  # 최소 256비트 BASE64 인코딩된 문자열
```

#### JWT Secret 생성 방법

**옵션 1: OpenSSL 사용 (macOS/Linux)**
```bash
openssl rand -base64 64
```

**옵션 2: 온라인 생성기**
- https://www.allkeysgenerator.com/Random/Security-Encryption-Key-Generator.aspx
- 256-bit 선택 후 BASE64로 인코딩

**옵션 3: 직접 생성 (Python)**
```python
import base64
import secrets
key = base64.b64encode(secrets.token_bytes(64)).decode()
print(key)
```

### 3. 프로젝트 빌드 및 실행

#### 빌드
```bash
cd user-service
./gradlew clean build --no-build-cache
```

#### 실행
```bash
./gradlew bootRun
```

또는 JAR 파일 실행:
```bash
java -jar build/libs/car-user-management-0.0.1-SNAPSHOT.jar
```

### 4. API 테스트

서버가 시작되면 (`http://localhost:8080`):

#### 헬스 체크
```bash
curl http://localhost:8080/api/auth/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "message": "Spring Boot User Management API",
  "version": "1.0.0"
}
```

#### 회원가입
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "phoneNumber": "010-1234-5678"
  }'
```

**비밀번호 규칙:**
- 최소 8자
- 영문자 포함
- 숫자 포함
- 특수문자 포함 (@$!%*#?&)

#### 로그인
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

**응답 예시:**
```json
{
  "success": true,
  "message": "로그인 성공",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 🔒 보안 주의사항

### ⚠️ 절대 커밋하지 말 것:
- `application.yml` (실제 비밀번호 포함)
- 데이터베이스 파일
- `.env` 파일
- 빌드 결과물 (`build/`, `target/`)

### ✅ Git에 포함해야 할 것:
- `application.yml.example` (템플릿)
- `setup_mysql.sql` (DB 스키마)
- 소스 코드
- README 및 문서

## 🐛 문제 해결

### MySQL 연결 실패
```
Access denied for user 'root'@'localhost'
```
**해결:** `application.yml`의 MySQL 비밀번호를 확인하세요.

### 포트 8080이 이미 사용 중
```
Port 8080 is already in use
```
**해결:**
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8080

# 프로세스 종료
kill -9 PID
```

또는 `application.yml`에서 포트 변경:
```yaml
server:
  port: 8081
```

### 순환 참조 에러
```
Circular dependency detected
```
**해결:** `application.yml`에 다음이 있는지 확인:
```yaml
spring:
  main:
    allow-circular-references: true
```

## 📚 추가 문서

- [API 테스트 결과](../API_TEST_RESULTS.md)
- [Spring Boot 완성 가이드](../SPRING_BOOT_COMPLETE.md)
- [프로젝트 아키텍처](../docs/ARCHITECTURE.md)

## 🤝 협업 가이드

### 브랜치 전략
- `main`: 안정 버전
- `develop`: 개발 버전
- `feature/*`: 새 기능 개발

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
refactor: 코드 리팩토링
test: 테스트 추가/수정
```

## 💬 문의

문제가 발생하면 이슈를 생성하거나 팀원에게 문의하세요.

