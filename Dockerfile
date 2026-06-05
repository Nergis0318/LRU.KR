# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# libvalkey is source-only (Rust); native headers cover lxml/pillow fallback builds
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cargo \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable


FROM python:3.14-slim-trixie AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        libxml2 \
        libxslt1.1 \
        zlib1g \
        libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 999 app \
    && useradd --system --gid 999 --uid 999 --create-home app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app main.py src templates static ./

USER app

EXPOSE 2001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:2001/ || exit 1

CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "4"]
