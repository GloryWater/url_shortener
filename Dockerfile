FROM python:3.12-slim

WORKDIR /app

# Установка uv и uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Настройки uv для Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Копируем ТОЛЬКО файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без самого кода проекта)
# Это создаст слой, который будет кэшироваться, пока не изменятся зависимости
RUN uv sync --frozen --no-dev --no-install-project

# Теперь копируем остальной код
COPY src/ ./src/
COPY index.html ./

# Устанавливаем сам проект (если он прописан в pyproject.toml)
RUN uv sync --frozen --no-dev

# Чтобы не писать "uv run" при старте, добавляем .venv в PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8001

# Запуск напрямую через uvicorn (uvrun уже не обязателен благодаря PATH)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
