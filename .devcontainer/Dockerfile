# ============================================================
# Development Container
# Python + Java + Node.js 통합 개발 환경
# ============================================================

FROM mcr.microsoft.com/devcontainers/base:ubuntu

# 비대화형 설치 설정
ENV DEBIAN_FRONTEND=noninteractive

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3.11 \
    python3.11-venv \
    python3-pip \
    # Java
    openjdk-17-jdk \
    # Node.js
    nodejs \
    npm \
    # 빌드 도구
    build-essential \
    git \
    curl \
    wget \
    # 네트워크 도구
    iputils-ping \
    netcat-openbsd \
    # 기타
    vim \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Python 기본 설정
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Node.js 최신 버전 (n 사용)
RUN npm install -g n && n 20 && npm install -g pnpm

# Gradle 설치
ENV GRADLE_VERSION=8.5
RUN wget -q https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -O /tmp/gradle.zip && \
    unzip -d /opt /tmp/gradle.zip && \
    rm /tmp/gradle.zip && \
    ln -s /opt/gradle-${GRADLE_VERSION}/bin/gradle /usr/local/bin/gradle

# Python 패키지 설치
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# 작업 디렉토리
WORKDIR /workspace

# 사용자 설정
USER vscode

# 환경 변수
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin:/opt/gradle-${GRADLE_VERSION}/bin
ENV PYTHONPATH=/workspace:/workspace/ml-service
