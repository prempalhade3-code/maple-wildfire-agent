# ---------------------------------------------------------
# Base image – slim Python 3.11 (same as the original build)
# ---------------------------------------------------------
FROM python:3.11-slim

# Install the system packages needed for GDAL / PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non‑root user (safer)
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID appgroup && \
    useradd -m -u $UID -g $GID -s /bin/bash appuser
USER appuser

# Working directory inside the container
WORKDIR /app

# Copy the backend dependency files first – this caches the dependency install layer
COPY backend/pyproject.toml backend/poetry.lock* ./

# Install Poetry (the same version you used before)
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.7.1 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install Python dependencies without creating a virtualenv
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# The root image runs the backend, just like docker compose.
COPY backend/ ./

# Expose the FastAPI port (default 8000)
EXPOSE 8000

# Default command – run the API with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
