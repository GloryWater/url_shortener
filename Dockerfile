FROM python:3.12-slim

WORKDIR /app

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install netcat for health checks
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# UV settings for Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy ONLY dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (without project code)
# This creates a layer that will be cached until dependencies change
RUN uv sync --frozen --no-dev --no-install-project

# Now copy the rest of the code
COPY src/ ./src/
COPY index.html ./
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Install the project itself (if specified in pyproject.toml)
RUN uv sync --frozen --no-dev

# To avoid typing "uv run" at startup, add .venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

# Use entrypoint script to run migrations before starting the app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
