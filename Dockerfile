FROM python:3.12-slim

WORKDIR /app

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Копирование файлов проекта
COPY pyproject.toml uv.lock* ./

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Копирование исходного кода
COPY src/ ./src/
COPY index.html ./

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Экспортируемый порт
EXPOSE 8000

# Запуск приложения
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
