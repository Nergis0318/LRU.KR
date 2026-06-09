FROM ghcr.io/astral-sh/uv:debian AS build

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY --from=build /app .

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 2001

ENTRYPOINT ["hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "4"]
