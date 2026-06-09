FROM ghcr.io/astral-sh/uv:latest AS build

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY --from=build /app .

EXPOSE 2001

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["uv", "run", "hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "4"]
