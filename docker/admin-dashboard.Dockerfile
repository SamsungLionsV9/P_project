# ============================================================
# Admin Dashboard Dockerfile (React/Vite)
# 
# 빌드: docker build -f docker/admin-dashboard.Dockerfile -t carsentix-admin ./admin-dashboard
# 실행: docker run -p 3001:3001 carsentix-admin
# ============================================================

FROM node:20-alpine

# pnpm 설치 (더 빠른 패키지 관리)
RUN npm install -g pnpm

WORKDIR /app

# 의존성 파일 먼저 복사 (캐시 활용)
COPY package*.json ./
RUN pnpm install --frozen-lockfile 2>/dev/null || npm install

# 소스 코드 복사
COPY . .

# 환경 변수
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:8000/api

# 포트 노출
EXPOSE 3001

# 개발 서버 실행 (핫 리로드 지원)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]
