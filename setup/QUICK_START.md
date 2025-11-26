# 🚀 Quick Start (협업자용 빠른 시작 가이드)

프로젝트를 5분 안에 실행하기 위한 가이드입니다.

---

## 📋 사전 요구사항

| 항목 | 버전 | 확인 명령어 |
|------|------|------------|
| Java | 17+ | `java -version` |
| MySQL | 8.0+ | `mysql --version` |
| Python | 3.9+ | `python --version` |
| Git | 최신 | `git --version` |

---

## 🔥 1. 프로젝트 클론

```bash
git clone https://github.com/SamsungLionsV9/P_project.git
cd P_project
```

---

## 🗄️ 2. MySQL 데이터베이스 설정

```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 생성 (SQL 파일 실행)
source setup/setup_mysql.sql;

# 소셜 로그인용 테이블 업데이트 (선택)
source setup/oauth2_schema_update.sql;

exit;
```

---

## ⚙️ 3. user-service 설정 (Spring Boot)

### 3-1. application.yml 생성

```bash
cp setup/application.yml.example user-service/src/main/resources/application.yml
```

### 3-2. 비밀번호 수정

`user-service/src/main/resources/application.yml` 열고 수정:

```yaml
spring:
  datasource:
    password: YOUR_MYSQL_PASSWORD  # ← 본인 MySQL 비밀번호
```

### 3-3. 서버 실행

```bash
cd user-service

# Java 17 설정 (Mac)
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# 빌드 & 실행
./gradlew bootRun
```

### 3-4. 테스트

```bash
# 헬스 체크
curl http://localhost:8080/api/auth/health

# 회원가입 테스트
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test123!"}'
```

---

## 🤖 4. ml-service 설정 (FastAPI)

### 4-1. 의존성 설치

```bash
cd ml-service
pip install -r requirements.txt
```

### 4-2. 서버 실행

```bash
# 프로젝트 루트에서
cd ..
python -m uvicorn ml-service.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4-3. 테스트

```bash
# 헬스 체크
curl http://localhost:8000/api/health

# 가격 예측 테스트
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"brand":"현대","model":"그랜저","year":2022,"mileage":35000,"fuel":"가솔린"}'
```

---

## 🌐 5. 서비스 포트 정리

| 서비스 | 포트 | 용도 |
|--------|------|------|
| user-service | 8080 | 사용자 인증/관리 (Spring Boot) |
| ml-service | 8000 | ML 가격 예측/타이밍 분석 (FastAPI) |

---

## 🔐 6. 소셜 로그인 설정 (선택)

소셜 로그인을 사용하려면 각 플랫폼에서 API 키를 발급받아야 합니다.

### Google
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. OAuth 2.0 클라이언트 ID 생성
3. 환경 변수 설정:
```bash
export GOOGLE_CLIENT_ID=your-client-id
export GOOGLE_CLIENT_SECRET=your-client-secret
```

### Naver
1. [Naver Developers](https://developers.naver.com) 접속
2. 애플리케이션 등록
3. 환경 변수 설정:
```bash
export NAVER_CLIENT_ID=your-client-id
export NAVER_CLIENT_SECRET=your-client-secret
```

### Kakao
1. [Kakao Developers](https://developers.kakao.com) 접속
2. 애플리케이션 등록
3. 환경 변수 설정:
```bash
export KAKAO_CLIENT_ID=your-client-id
export KAKAO_CLIENT_SECRET=your-client-secret
```

---

## 🐛 자주 발생하는 문제

### MySQL 연결 실패
```
Access denied for user 'root'@'localhost'
```
→ `application.yml`의 비밀번호 확인

### 포트 이미 사용 중
```bash
# 포트 확인
lsof -i :8080

# 프로세스 종료
kill -9 PID
```

### Java 버전 문제
```bash
# Mac에서 Java 17 설치
brew install openjdk@17

# 환경 변수 설정
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

---

## 📁 프로젝트 구조

```
P_project/
├── user-service/          # Spring Boot 사용자 서비스
│   └── src/main/
│       ├── java/         # Java 소스
│       └── resources/    # application.yml
├── ml-service/            # FastAPI ML 서비스
│   ├── main.py           # 메인 API
│   ├── services/         # 비즈니스 로직
│   └── schemas/          # API 스키마
├── models/                # ML 모델 파일 (.pkl)
├── data/                  # 데이터 파일
├── setup/                 # 설정 가이드
└── docs/                  # 문서
```

---

## 📚 추가 문서

- [API 명세서](API_SPECIFICATION.md)
- [마이크로서비스 가이드](MICROSERVICES_GUIDE.md)
- [OAuth2 설정 가이드](OAUTH2_SETUP_GUIDE.md)
- [상세 설정 가이드](SETUP_GUIDE.md)

---

## 💬 문의

문제 발생 시 GitHub Issue를 생성하거나 팀원에게 문의하세요!

