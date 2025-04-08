FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

EXPOSE 2001

ENTRYPOINT ["uv", "run", "hypercorn", "main:app", "--bind", "0.0.0.0:2001", "-w", "10"]
