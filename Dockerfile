## Multi-stage (simple) Dockerfile for running the Pohualli web UI
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (minimal). Add build-essential if later you need compiled deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy project (python package + build metadata)
COPY pyproject.toml /app/
COPY pohualli /app/pohualli

# Install project with web extras
RUN pip install --upgrade pip && pip install .[web]

EXPOSE 8000

# Default command runs the FastAPI app
CMD ["uvicorn", "pohualli.webapp:app", "--host", "0.0.0.0", "--port", "8000"]
