# ============================================================
# ML Service Dockerfile (Python/FastAPI)
# 
# 빌드: docker build -f docker/ml-service.Dockerfile -t carsentix-ml .
# 실행: docker run -p 8000:8000 carsentix-ml
# ============================================================

FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 먼저 복사 (캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ml-service/ ./ml-service/
COPY src/ ./src/
COPY config/ ./config/
COPY run_server.py .
COPY .env* ./

# 데이터 및 모델 디렉토리 (볼륨 마운트용)
RUN mkdir -p /app/data /app/models /app/logs

# 환경 변수 설정
ENV PYTHONPATH=/app:/app/ml-service
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 실행 명령
CMD ["python", "run_server.py"]
