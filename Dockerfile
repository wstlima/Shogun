# ── Stage 1: Build Tenshu UI ──────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python Runtime ───────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="AlphaHorizon AI"
LABEL description="Shogun — GUI-first AI agent framework (The Tenshu)"

# System deps (curl for healthcheck; playwright/chromium deps for Mado browser automation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[office]"

# Mado browser engine (Playwright Chromium) — same as install.sh step 4
RUN python -m playwright install chromium

# Copy application code
COPY shogun/ ./shogun/
COPY main.py ./main.py
COPY version.json ./version.json
COPY .env.example ./.env.example
# shogun/__main__.py auto-generates .env from .env.example (or sensible
# defaults, including API_HOST=0.0.0.0/API_PORT=8000) on first run if
# missing, and auto-bootstraps the database — no manual .env needed here.

# Copy built frontend from stage 1 (PROJECT_ROOT/frontend/dist, see shogun/app.py)
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Non-root user (see gensui/Dockerfile for the same pattern / migration notes)
RUN groupadd --gid 1000 shogun \
    && useradd --uid 1000 --gid shogun --shell /bin/bash --create-home shogun \
    && mkdir -p /app/data /app/logs /app/configs /app/vault \
    && chown -R shogun:shogun /app
USER shogun

EXPOSE 8000

VOLUME /app/data

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENV API_HOST=0.0.0.0
ENV API_PORT=8000

CMD ["python", "-m", "shogun"]
