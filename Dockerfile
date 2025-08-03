FROM ghcr.io/astral-sh/uv:debian-slim
# apt-get으로 supervisor 설치 (더 안정적)
RUN apt-get update && \
    apt-get install -y supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN uv sync --frozen

CMD ["supervisord", "-c", "supervisord.conf"]
