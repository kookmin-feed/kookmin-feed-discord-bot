FROM ghcr.io/astral-sh/uv:python3.10-alpine

WORKDIR /app
COPY . .
RUN uv sync --frozen

CMD ["uv", "run", "python", "main.py"]
