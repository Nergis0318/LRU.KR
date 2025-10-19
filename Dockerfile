FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY . .

RUN apk update --no-cache && apk upgrade --no-cache && apk add --no-cache rust cargo build-base

RUN uv sync --frozen --no-cache

EXPOSE 2001

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random

ENTRYPOINT ["uv", "run", "hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "1"]
