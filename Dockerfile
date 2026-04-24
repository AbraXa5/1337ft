FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Compile bytecode for faster cold starts; copy deps instead of symlinking
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    FLASK_APP=1337ft/__main__.py \
    FLASK_DEBUG=0 \
    FLASK_RUN_PORT=8008

# Install dependencies first so this layer is cached unless lockfile changes
COPY uv.lock pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application source
COPY ./1337ft ./1337ft

EXPOSE 8008

CMD ["uv", "run", "flask", "run", "--host=0.0.0.0"]
