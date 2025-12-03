# ============================================================
# Car-Sentix Makefile
# 
# 사용법:
#   make start     - 전체 서비스 시작
#   make stop      - 전체 서비스 중지
#   make logs      - 로그 확인
#   make build     - 이미지 재빌드
#   make clean     - 컨테이너/이미지 정리
# ============================================================

.PHONY: start stop restart build logs clean help dev-setup test

# 기본 명령
help:
	@echo "Car-Sentix Docker 명령어"
	@echo "========================"
	@echo "  make start    - 전체 서비스 시작"
	@echo "  make stop     - 전체 서비스 중지"
	@echo "  make restart  - 서비스 재시작"
	@echo "  make build    - 이미지 재빌드"
	@echo "  make logs     - 전체 로그 확인"
	@echo "  make logs-ml  - ML 서비스 로그"
	@echo "  make logs-user - User 서비스 로그"
	@echo "  make clean    - 컨테이너/이미지 정리"
	@echo "  make dev-setup - 개발 환경 초기 설정"

# 서비스 시작
start:
	@echo "🚀 서비스 시작 중..."
	docker-compose up -d
	@echo "✓ 서비스 시작 완료"
	@docker-compose ps

# 서비스 중지
stop:
	@echo "🛑 서비스 중지 중..."
	docker-compose down
	@echo "✓ 서비스 중지 완료"

# 서비스 재시작
restart: stop start

# 이미지 빌드
build:
	@echo "📦 Docker 이미지 빌드 중..."
	docker-compose build --no-cache
	@echo "✓ 빌드 완료"

# 로그 확인
logs:
	docker-compose logs -f

logs-ml:
	docker-compose logs -f ml-service

logs-user:
	docker-compose logs -f user-service

logs-admin:
	docker-compose logs -f admin-dashboard

# 개별 서비스 시작
ml:
	docker-compose up -d ml-service

user:
	docker-compose up -d user-service

admin:
	docker-compose up -d admin-dashboard

# 정리
clean:
	@echo "🧹 Docker 리소스 정리 중..."
	docker-compose down -v --rmi local
	@echo "✓ 정리 완료"

# 개발 환경 초기 설정
dev-setup:
	@echo "🔧 개발 환경 설정 중..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✓ .env 파일 생성됨"; fi
	@mkdir -p data logs models
	@echo "✓ 디렉토리 생성됨"
	@echo "✓ 개발 환경 설정 완료"

# 상태 확인
status:
	@docker-compose ps

# 셸 접속
shell-ml:
	docker-compose exec ml-service bash

shell-user:
	docker-compose exec user-service sh

shell-admin:
	docker-compose exec admin-dashboard sh
