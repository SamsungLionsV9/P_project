# ============================================================
# Docker 기반 서비스 시작 스크립트 (Windows PowerShell)
# 
# 사용법:
#   .\scripts\docker-start.ps1        # 전체 서비스 시작
#   .\scripts\docker-start.ps1 ml     # ML 서비스만
#   .\scripts\docker-start.ps1 build  # 이미지 재빌드 후 시작
# ============================================================

param(
    [string]$Service = "all"
)

# 프로젝트 루트로 이동
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host "`n🚀 Car-Sentix Docker 시작" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# 환경 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env 파일이 없습니다. .env.example에서 복사합니다." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env 파일 생성됨" -ForegroundColor Green
}

# Docker 실행 확인
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker가 실행 중이 아닙니다. Docker Desktop을 시작해주세요." -ForegroundColor Red
    exit 1
}

# 서비스 시작
switch ($Service.ToLower()) {
    "build" {
        Write-Host "📦 Docker 이미지 빌드 중..." -ForegroundColor Blue
        docker-compose build --no-cache
        Write-Host "🔄 서비스 시작 중..." -ForegroundColor Blue
        docker-compose up -d
    }
    "ml" {
        Write-Host "🤖 ML Service 시작 중..." -ForegroundColor Blue
        docker-compose up -d ml-service
    }
    "user" {
        Write-Host "👤 User Service 시작 중..." -ForegroundColor Blue
        docker-compose up -d user-service
    }
    "admin" {
        Write-Host "📊 Admin Dashboard 시작 중..." -ForegroundColor Blue
        docker-compose up -d admin-dashboard
    }
    default {
        Write-Host "🔄 전체 서비스 시작 중..." -ForegroundColor Blue
        docker-compose up -d
    }
}

# 상태 확인
Write-Host "`n✓ 서비스 상태:" -ForegroundColor Green
docker-compose ps

Write-Host "`n📌 서비스 URL:" -ForegroundColor Green
Write-Host "   - ML Service:      http://localhost:8000"
Write-Host "   - User Service:    http://localhost:8080"
Write-Host "   - Admin Dashboard: http://localhost:3001"
Write-Host "`n📝 로그 확인: docker-compose logs -f [service_name]" -ForegroundColor Blue
Write-Host "🛑 중지: docker-compose down" -ForegroundColor Blue
