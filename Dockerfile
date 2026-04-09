# ─── Stage 1: Builder ──────────────────────────

FROM python:3.11-slim AS builder
# ^ Start from official Python 3.11 (slim = no extra tools)
# ^ "AS builder" names this stage so we can reference it later

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# ^ Install C compiler (build-essential) and PostgreSQL headers (libpq-dev)
# ^ rm -rf cleans the apt cache to keep the layer small

WORKDIR /app
# ^ Like "cd /app" — all future commands run from here

COPY requirments/ requirments/
# ^ Copy ONLY requirements first (not all code)
# ^ WHY? Docker caches layers. If requirements haven't changed,
# ^ Docker skips pip install on next build — saves 60+ seconds

RUN pip install --no-cache-dir -r requirments/production.txt
# ^ Install all Python packages
# ^ --no-cache-dir: don't store pip's download cache (smaller image)


# ─── Stage 2: Production ──────────────────────

FROM python:3.11-slim
# ^ Fresh start! No gcc, no build tools — clean slate

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
# ^ Only the PostgreSQL RUNTIME library (not the dev headers)

RUN useradd --create-home appuser
# ^ Create a non-root user (security: if the app is hacked,
# ^ the attacker can't do root-level damage)

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# ^ Copy the installed Python packages FROM the builder stage
# ^ This is the magic of multi-stage: we get compiled packages
# ^ without carrying the 300MB compiler

COPY . .
# ^ Copy your project code (filtered by .dockerignore)

RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app
# ^ Create staticfiles dir and give ownership to appuser

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# ^ Copy and make the startup script executable

USER appuser
# ^ Switch to non-root user from here on

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
# ^ UNBUFFERED: print() and logs appear immediately in `docker logs`
# ^ DONTWRITEBYTECODE: don't create .pyc files (unnecessary in container)

EXPOSE 8000
# ^ Document that this container listens on port 8000
# ^ (doesn't actually open the port — that's done in docker-compose)

ENTRYPOINT ["/entrypoint.sh"]
# ^ When the container starts, run this script
