# ============================================================
# User Service Dockerfile (Spring Boot)
# 
# 빌드: docker build -f docker/user-service.Dockerfile -t carsentix-user ./user-service
# 실행: docker run -p 8080:8080 carsentix-user
# ============================================================

# === Build Stage ===
FROM gradle:8.5-jdk17 AS builder

WORKDIR /build

# Gradle 캐시 활용을 위해 의존성 파일 먼저 복사
COPY build.gradle settings.gradle ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon || true

# 소스 코드 복사 및 빌드
COPY src ./src
RUN gradle bootJar --no-daemon -x test

# === Runtime Stage ===
FROM eclipse-temurin:17-jre-alpine

# 보안: 비root 사용자로 실행
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -D appuser

WORKDIR /app

# 빌드된 JAR 복사
COPY --from=builder /build/build/libs/*.jar app.jar

# 데이터 디렉토리 생성 (H2 DB 저장용)
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# 비root 사용자로 전환
USER appuser

# 환경 변수
ENV JAVA_OPTS="-Xmx512m -Xms256m"
ENV SPRING_PROFILES_ACTIVE=docker

# 포트 노출
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# 실행 명령
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
