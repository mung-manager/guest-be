# Dockerfile.base

# Python 3.11 Debian Bullseye 기반 이미지 사용
FROM --platform=linux/arm64 python:3.11 AS base

# Python 설정 최적화
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/project/

# pycurl 설정을 위한 환경 변수 설정
ENV PYCURL_SSL_LIBRARY=openssl \
    PYCURL_CURL_CONFIG=/usr/bin/curl-config \
    CPPFLAGS="-I/usr/include/openssl" \
    LDFLAGS="-L/usr/lib/ssl"

# 시스템 라이브러리 업데이트 및 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libcurl4-openssl-dev \
    libssl-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 버전 및 경로 설정
RUN pip install --upgrade pip setuptools wheel && \
    pip install poetry==1.8.2 && \
    poetry config virtualenvs.create false

# 작업 디렉토리 설정
WORKDIR /opt/project/

# 의존성 파일 복사
COPY pyproject.toml poetry.lock ./

# 패키지 설치
RUN pip install --no-cache-dir --compile pycurl \
    && poetry install
