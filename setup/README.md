# 🚀 팀원 온보딩 가이드

**중고차 가격 예측 시스템 - 빠른 시작 가이드**

이 폴더에는 프로젝트를 시작하는데 필요한 **모든 설정 문서**가 있습니다!

---

## 📋 목차

1. [빠른 시작](#-빠른-시작)
2. [문서 읽는 순서](#-문서-읽는-순서)
3. [파일 설명](#-파일-설명)
4. [자주 묻는 질문](#-자주-묻는-질문)

---

## ⚡ 빠른 시작

### 1️⃣ 필수 소프트웨어 설치
- [ ] **Java 17 이상**
- [ ] **MySQL 8.0**
- [ ] **Python 3.8+**
- [ ] **Git**

### 2️⃣ 프로젝트 클론
```bash
git clone https://github.com/SamsungLionsV9/P_project.git
cd P_project
```

### 3️⃣ 데이터베이스 설정
```bash
# MySQL 접속
mysql -u root -p

# DB 생성 스크립트 실행
source setup/setup_mysql.sql
```

### 4️⃣ User Service 설정
```bash
cd user-service/src/main/resources

# 설정 파일 복사
cp application.yml.example application.yml

# application.yml 편집하여 MySQL 비밀번호 입력
nano application.yml  # 또는 vscode로 열기
```

### 5️⃣ 서비스 실행

**터미널 1: User Service (포트 8080)**
```bash
cd user-service
./gradlew bootRun
```

**터미널 2: ML Service (포트 8000)**
```bash
cd ml-service
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6️⃣ 확인
```bash
# User Service
curl http://localhost:8080/api/auth/health

# ML Service
curl http://localhost:8000/api/health
```

✅ 둘 다 응답이 오면 성공!

---

## 📖 문서 읽는 순서

팀원이라면 **이 순서대로** 읽어주세요! 👇

### 1단계: 전체 구조 이해 (10분)
```
📄 MICROSERVICES_GUIDE.md
```
- 시스템이 어떻게 구성되어 있는지
- 2개 서비스의 역할
- 왜 이렇게 나눴는지

### 2단계: 로컬 환경 설정 (30분)
```
📄 SETUP_GUIDE.md
```
- MySQL 설정
- application.yml 설정
- JWT Secret 생성
- 서비스 실행
- 문제 해결

### 3단계: API 사용법 (필요시)
```
📄 API_SPECIFICATION.md
```
- 13개 API 엔드포인트
- 요청/응답 예제
- 프론트엔드 통합 방법

---

## 📁 파일 설명

### 🔧 설정 파일

| 파일 | 용도 | 필수 여부 |
|------|------|----------|
| **setup_mysql.sql** | MySQL DB 생성 스크립트 | ✅ 필수 |
| **application.yml.example** | Spring Boot 설정 템플릿 | ✅ 필수 |

**사용 방법:**
1. `application.yml.example` → `application.yml`로 복사
2. MySQL 비밀번호 입력
3. JWT Secret 생성 후 입력

---

### 📚 가이드 문서

| 문서 | 내용 | 읽는 시점 |
|------|------|----------|
| **MICROSERVICES_GUIDE.md** | 마이크로서비스 아키텍처 | 🥇 가장 먼저 |
| **SETUP_GUIDE.md** | 로컬 환경 설정 상세 가이드 | 🥈 두 번째 |
| **API_SPECIFICATION.md** | API 명세서 (13개 엔드포인트) | 🥉 개발 시 |

---

## ❓ 자주 묻는 질문

### Q1. MySQL 비밀번호를 어디에 입력하나요?
**A**: `user-service/src/main/resources/application.yml` 파일
```yaml
datasource:
  password: 여기에_본인_MySQL_비밀번호
```

### Q2. JWT Secret은 어떻게 생성하나요?
**A**: 터미널에서 실행
```bash
openssl rand -base64 64
```
생성된 문자열을 `application.yml`에 입력

### Q3. 포트가 이미 사용 중이라고 나와요
**A**: 
```bash
# 포트 사용 프로세스 확인
lsof -i :8080  # User Service
lsof -i :8000  # ML Service

# 프로세스 종료
kill -9 [PID]
```

### Q4. ML 모델이 없다고 나와요
**A**: 
```bash
cd src
python train_model_improved.py
```
20-30분 소요됩니다.

### Q5. User Service와 ML Service의 차이는?
**A**:
- **User Service (8080)**: 회원가입, 로그인, JWT 인증
- **ML Service (8000)**: 가격 예측, 타이밍 분석, AI 기능

### Q6. 두 서비스를 꼭 다 실행해야 하나요?
**A**: 
- 회원 기능만 테스트 → User Service만 실행
- 가격 예측만 테스트 → ML Service만 실행
- 전체 시스템 테스트 → 둘 다 실행

### Q7. Groq AI 기능은 어떻게 활성화하나요?
**A**: 프로젝트 루트에 `.env` 파일 생성
```bash
GROQ_API_KEY=your_groq_api_key_here
```
없어도 기본 기능은 작동합니다.

---

## 🔗 추가 리소스

### 📖 상세 문서
- [프로젝트 전체 개요](../README.md)
- [Spring Boot 완성 가이드](../SPRING_BOOT_COMPLETE.md)
- [API 테스트 결과](../API_TEST_RESULTS.md)
- [Groq AI 기능](../docs/GROQ_AI_FEATURES.md)

### 🌐 API 문서 (실행 후)
- **User Service**: 코드에서 확인
- **ML Service Swagger**: http://localhost:8000/docs
- **ML Service ReDoc**: http://localhost:8000/redoc

### 🐛 문제 발생 시
1. **SETUP_GUIDE.md**의 "문제 해결" 섹션 확인
2. GitHub Issues에 질문 등록
3. 팀 채널에 문의

---

## 📞 도움이 필요하신가요?

- **GitHub Issues**: https://github.com/SamsungLionsV9/P_project/issues
- **문서 개선 제안**: Pull Request 환영합니다!

---

## ✅ 체크리스트

설정을 완료했다면 체크해보세요!

- [ ] Java 17+ 설치 확인 (`java -version`)
- [ ] MySQL 설치 및 실행 (`mysql -u root -p`)
- [ ] `setup_mysql.sql` 실행 완료
- [ ] `application.yml` 생성 및 비밀번호 입력
- [ ] User Service 실행 성공 (포트 8080)
- [ ] ML Service 실행 성공 (포트 8000)
- [ ] 헬스체크 API 테스트 성공
- [ ] 회원가입 테스트 성공
- [ ] 가격 예측 테스트 성공

모두 체크했다면 🎉 **개발 시작 준비 완료!**

---

**마지막 업데이트**: 2025-11-24  
**버전**: 1.0  
**관리자**: 프로젝트 팀

