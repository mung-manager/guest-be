# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables to optimize Python setup
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set Poetry version and paths
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

# Install GDAL and PROJ
RUN apt-get update \
    && apt-get install -y binutils \
	libproj-dev \
	gdal-bin

# Install Poetry
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add Poetry binary to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Set working directory
RUN mkdir /app/
WORKDIR /app/

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN poetry install --without test

# Copy the rest of the application files
COPY . /app
