# ✅ Spring Boot 회원 관리 시스템 완성!

MySQL 연동 + JWT 인증 기반 로그인/로그아웃/회원가입/회원탈퇴 완성

---

## 🎉 구현 완료!

### ✅ 완성된 기능
1. ✅ **회원가입** - 이메일/비밀번호 검증
2. ✅ **로그인** - JWT 토큰 발급
3. ✅ **로그아웃** - 클라이언트 토큰 삭제
4. ✅ **회원 정보 조회** - JWT 인증
5. ✅ **회원 탈퇴** - 소프트 삭제
6. ✅ **JWT 인증/인가** - Spring Security
7. ✅ **MySQL 연동** - JPA/Hibernate
8. ✅ **입력 검증** - Bean Validation

---

## 📁 프로젝트 구조

```
user-service/
├── src/main/java/com/example/carproject/
│   ├── CarUserManagementApplication.java    # 메인 애플리케이션
│   │
│   ├── config/
│   │   └── SecurityConfig.java              # Spring Security 설정
│   │
│   ├── controller/
│   │   └── UserController.java              # REST API 컨트롤러
│   │       ├── POST /api/auth/signup        # 회원가입
│   │       ├── POST /api/auth/login         # 로그인
│   │       ├── POST /api/auth/logout        # 로그아웃
│   │       ├── GET  /api/auth/me            # 회원 정보 조회
│   │       └── DELETE /api/auth/me          # 회원 탈퇴
│   │
│   ├── dto/
│   │   ├── UserSignupDto.java               # 회원가입 요청
│   │   ├── UserLoginDto.java                # 로그인 요청
│   │   └── UserResponseDto.java             # 사용자 응답
│   │
│   ├── entity/
│   │   └── User.java                        # 사용자 엔티티
│   │
│   ├── repository/
│   │   └── UserRepository.java              # JPA Repository
│   │
│   ├── security/
│   │   └── JwtAuthenticationFilter.java     # JWT 인증 필터
│   │
│   └── service/
│       ├── UserService.java                 # 비즈니스 로직
│       └── JwtService.java                  # JWT 관리
│
├── src/main/resources/
│   └── application.yml                       # 설정 파일
│
├── build.gradle                              # Gradle 빌드 설정
├── settings.gradle                           # Gradle 설정
├── gradlew                                   # Gradle Wrapper (Unix)
├── setup_mysql.sql                           # MySQL 초기화 스크립트
├── test_api.sh                               # API 테스트 스크립트
└── README.md                                 # 상세 문서
```

---

## 🚀 빠른 시작

### 1️⃣ MySQL 데이터베이스 생성

```bash
cd /Users/jeong-uiyeob/Downloads/used-car-price-predictor-main/user-service

# MySQL 실행 (macOS)
mysql.server start

# 데이터베이스 생성
mysql -u root -p < setup_mysql.sql
```

### 2️⃣ 설정 파일 수정

`src/main/resources/application.yml`에서 MySQL 비밀번호 변경:

```yaml
spring:
  datasource:
    password: your_actual_password  # 실제 MySQL 비밀번호로 변경!
```

### 3️⃣ 애플리케이션 실행

```bash
# 방법 1: Gradle로 실행
./gradlew bootRun

# 방법 2: 빌드 후 실행
./gradlew build
java -jar build/libs/car-user-management-0.0.1-SNAPSHOT.jar
```

서버가 시작되면:
```
✅ http://localhost:8080 에서 실행 중
```

---

## 🧪 API 테스트

### 자동 테스트 스크립트

```bash
./test_api.sh
```

### 수동 테스트 (cURL)

#### 1. 회원가입
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!",
    "phoneNumber": "010-1234-5678"
  }'
```

**응답**:
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phoneNumber": "010-1234-5678",
    "role": "USER",
    "createdAt": "2025-11-24T15:00:00"
  }
}
```

#### 2. 로그인
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }'
```

**응답**:
```json
{
  "success": true,
  "message": "로그인 성공",
  "token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. 회원 정보 조회
```bash
# JWT 토큰 저장
TOKEN="여기에_로그인_시_받은_토큰_붙여넣기"

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. 회원 탈퇴
```bash
curl -X DELETE http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 데이터베이스 확인

```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 선택
USE car_database;

# 테이블 확인
SHOW TABLES;

# 사용자 조회
SELECT * FROM users;

# 테이블 구조
DESC users;
```

**users 테이블 구조**:
```
+---------------+--------------+------+-----+
| Field         | Type         | Null | Key |
+---------------+--------------+------+-----+
| id            | bigint       | NO   | PRI |
| username      | varchar(50)  | NO   | UNI |
| email         | varchar(100) | NO   | UNI |
| password      | varchar(255) | NO   |     |
| phone_number  | varchar(20)  | YES  |     |
| role          | varchar(10)  | YES  |     |
| is_active     | bit(1)       | NO   |     |
| created_at    | datetime(6)  | NO   |     |
| updated_at    | datetime(6)  | NO   |     |
+---------------+--------------+------+-----+
```

---

## 🔐 보안 설정

### JWT 설정
- **비밀 키**: 256비트 이상 (application.yml에서 변경 필수!)
- **만료 시간**: 24시간
- **알고리즘**: HS256

### 비밀번호 규칙
- 최소 8자 이상
- 영문, 숫자, 특수문자 포함 필수

### CORS 설정
- 현재: 모든 도메인 허용 (*)
- 운영 환경: 특정 도메인만 허용하도록 변경 필요

---

## 🎯 다음 단계

### 1. ML 서비스와 사용자 서비스 통합
```bash
# ML 서비스 실행 (FastAPI)
cd ml-service
python -m uvicorn main:app --port 8000

# 사용자 서비스 실행 (Spring Boot)
cd user-service
./gradlew bootRun  # 포트 8080
```

### 2. 프론트엔드 연동
- React/Vue.js 개발
- JWT 토큰 저장 (localStorage/sessionStorage)
- API 호출 통합

### 3. CSV 데이터 MySQL 연동
```bash
# CSV → MySQL import 스크립트 실행
python scripts/import_csv_to_mysql.py
```

---

## 📦 배포

### Docker 컨테이너화

`Dockerfile`:
```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

빌드 및 실행:
```bash
# 빌드
./gradlew build
docker build -t car-user-management .

# 실행
docker run -p 8080:8080 car-user-management
```

---

## 🐛 문제 해결

### 1. MySQL 연결 오류
```
Unable to connect to database
```

**해결책**:
1. MySQL이 실행 중인지 확인
2. `application.yml`의 비밀번호 확인
3. 데이터베이스 `car_database` 존재 확인

### 2. JWT 오류
```
JWT signature does not match
```

**해결책**:
- `application.yml`의 JWT secret 키가 256비트 이상인지 확인

### 3. 포트 충돌
```
Port 8080 is already in use
```

**해결책**:
```yaml
# application.yml
server:
  port: 8081  # 포트 변경
```

---

## 📚 상세 문서

- **user-service/README.md** - 전체 API 문서 및 사용법 (삭제됨)
- **user-service/setup_mysql.sql** - MySQL 초기화 스크립트
- **user-service/test_api.sh** - 자동 API 테스트 스크립트

---

## 🎉 완성!

**모든 로직이 구현되었습니다!**

✅ 회원가입  
✅ 로그인  
✅ 로그아웃  
✅ 회원 정보 조회  
✅ 회원 탈퇴  
✅ JWT 인증  
✅ MySQL 연동  

---

**구현 완료 일시**: 2025년 11월 24일  
**기술 스택**: Spring Boot 3.2, MySQL 8.0, JWT, Spring Security  
**프로젝트**: 중고차 회원 관리 시스템

