# 🐳 Car-Sentix Docker 개발 환경

> **어디서든 동일한 개발 환경으로 바로 시작!**  
> Docker와 VS Code만 있으면 됩니다.

## 📋 사전 요구사항

| 도구 | 버전 | 설치 링크 |
|------|------|----------|
| Docker Desktop | 4.x+ | [다운로드](https://www.docker.com/products/docker-desktop) |
| VS Code | 최신 | [다운로드](https://code.visualstudio.com/) |
| Git | 2.x+ | [다운로드](https://git-scm.com/) |

## 🚀 빠른 시작 (5분 안에 개발 시작)

### 방법 1: VS Code Dev Container (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/SamsungLionsV9/P_project.git
cd P_project

# 2. VS Code로 열기
code .

# 3. VS Code에서 "Reopen in Container" 선택
#    (Ctrl+Shift+P → "Dev Containers: Reopen in Container")
```

### 방법 2: Docker Compose 직접 실행

```bash
# 1. 저장소 클론
git clone https://github.com/SamsungLionsV9/P_project.git
cd P_project

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력

# 3. 서비스 시작
docker-compose up -d

# 4. 서비스 확인
docker-compose ps
```

## 📦 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| ML Service | 8000 | Python/FastAPI - 가격 예측, 타이밍 분석 |
| User Service | 8080 | Spring Boot - 사용자 인증/관리 |
| Admin Dashboard | 3001 | React/Vite - 관리자 대시보드 |

## 🔧 주요 명령어

### Docker Compose

```bash
# 전체 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d ml-service

# 로그 확인
docker-compose logs -f              # 전체 로그
docker-compose logs -f ml-service   # ML 서비스 로그만

# 서비스 중지
docker-compose down

# 이미지 재빌드 후 시작
docker-compose up -d --build

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 셸 접속
docker-compose exec ml-service bash
```

### Make 명령어 (간편 버전)

```bash
make start    # 서비스 시작
make stop     # 서비스 중지
make restart  # 재시작
make logs     # 로그 확인
make build    # 이미지 재빌드
make clean    # 정리
```

### Windows PowerShell

```powershell
.\scripts\docker-start.ps1           # 전체 시작
.\scripts\docker-start.ps1 ml        # ML만 시작
.\scripts\docker-start.ps1 build     # 빌드 후 시작
```

## 🔐 환경 변수

`.env` 파일에 다음 API 키들을 설정하세요:

```env
# 필수
GROQ_API_KEY=your_groq_api_key      # AI 기능용
BOK_API_KEY=your_bok_api_key        # 경제 지표용

# 선택 (기본값 있음)
JWT_SECRET=your_secret_key          # 보안 키
```

## 🏗️ 프로젝트 구조

```
P_project/
├── .devcontainer/          # VS Code Dev Container 설정
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── docker-compose.devcontainer.yml
├── docker/                 # Docker 설정 파일
│   ├── ml-service.Dockerfile
│   ├── user-service.Dockerfile
│   └── admin-dashboard.Dockerfile
├── docker-compose.yml      # 메인 Docker Compose
├── .env.example            # 환경 변수 템플릿
├── Makefile               # 간편 명령어
├── ml-service/            # Python ML 서비스
├── user-service/          # Spring Boot 서비스
├── admin-dashboard/       # React 대시보드
└── flutter_app/           # Flutter 앱 (로컬 실행)
```

## 🔄 개발 워크플로우

### 코드 변경 반영

| 서비스 | 핫 리로드 | 수동 재시작 필요 |
|--------|---------|---------------|
| ML Service | ❌ | `docker-compose restart ml-service` |
| Admin Dashboard | ✅ | 자동 반영 (Vite HMR) |
| User Service | ❌ | `docker-compose restart user-service` |

### 의존성 추가 시

```bash
# Python 패키지 추가 후
docker-compose build ml-service
docker-compose up -d ml-service

# Node.js 패키지 추가 후
docker-compose build admin-dashboard
docker-compose up -d admin-dashboard
```

## 🐛 트러블슈팅

### 포트 충돌

```bash
# 사용 중인 포트 확인 (Windows)
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs ml-service

# 클린 빌드
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### 볼륨 권한 문제 (Linux/Mac)

```bash
# 데이터 디렉토리 권한 설정
sudo chown -R $USER:$USER data/ logs/ models/
```

## 📊 헬스체크

모든 서비스는 헬스체크 엔드포인트를 제공합니다:

- ML Service: http://localhost:8000/health
- User Service: http://localhost:8080/actuator/health
- Admin Dashboard: http://localhost:3001

## 🔗 관련 문서

- [README.md](./README.md) - 프로젝트 개요
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 시스템 아키텍처
- [API 문서](http://localhost:8000/docs) - Swagger UI (ML Service 실행 후)
