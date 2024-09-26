# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables to optimize Python setup
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set Poetry version and paths
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV PATH="/opt/poetry-venv/bin:$PATH"

# Install system libraries needed for GDAL, PROJ, and pycurl with OpenSSL support
RUN apt-get update \
    && apt-get install -y binutils libproj-dev gdal-bin libcurl4-openssl-dev libssl-dev build-essential curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYCURL_SSL_LIBRARY=openssl
ENV PYCURL_CURL_CONFIG=/usr/bin/curl-config
ENV CPPFLAGS="-I/usr/include/openssl"
ENV LDFLAGS="-L/usr/lib/ssl"

# Install Poetry
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip==22.0 setuptools \
    && $POETRY_VENV/bin/pip install poetry==$POETRY_VERSION

# Set working directory
RUN mkdir /app
WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN poetry config virtualenvs.create false \
    && pip install --no-cache-dir --compile --install-option="--with-openssl" pycurl \
    && poetry install --without test

# Copy the rest of the application files
COPY . /app
