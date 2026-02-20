# ⚡ FastAPI URL Shortener (v2.0)

Высокопроизводительный сервис сокращения ссылок с современным асинхронным стеком, аналитикой и элегантным фронтендом.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Tests](https://img.shields.io/badge/tests-52%20passed-green?style=for-the-badge&logo=pytest)
![Coverage](https://img.shields.io/codecov/c/github/GloryWater/url_shortener?style=for-the-badge&logo=codecov)
![CI/CD](https://img.shields.io/github/actions/workflow/status/GloryWater/url_shortener/ci-cd.yaml?style=for-the-badge&logo=github-actions)

---

## 🌟 Особенности v2.0

- **Асинхронный backend** на FastAPI + Uvicorn
- **PostgreSQL 17** с асинхронным драйвером `asyncpg`
- **SQLAlchemy 2.0** с async session
- **Валидация данных** через Pydantic v2 + pydantic-settings
- **Миграции БД** через Alembic
- **Rate Limiting** для защиты от злоупотреблений
- **Аналитика переходов** с подсчетом кликов
- **Кастомные slug** и срок действия ссылок
- **API версионирование** (`/api/v1/`)
- **Health check** endpoint
- **Security headers** middleware
- **Структурированное логирование** (JSON для production)
- **Стильный фронтенд** (Vanilla JS + CSS Soft UI)
- **Покрытие тестами** (52 теста + pytest + httpx)

---

## 🛠️ Технологический стек

| Категория       | Технологии                                      |
|-----------------|-------------------------------------------------|
| **Backend**     | FastAPI, Uvicorn                                |
| **Database**    | PostgreSQL 17, SQLAlchemy 2.0, asyncpg, Alembic |
| **Config**      | pydantic-settings                               |
| **Testing**     | pytest, pytest-asyncio, pytest-cov, httpx       |
| **Frontend**    | Vanilla JavaScript, CSS3 (Soft UI)              |
| **DevOps**      | Docker, Docker Compose, GitHub Actions          |
| **Security**    | slowapi (rate limiting), security headers       |
| **Logging**     | python-json-logger                              |

---

## 📦 Структура проекта

```
url_shortener/
├── src/
│   ├── main.py           # Точка входа API (FastAPI app)
│   ├── service.py        # Бизнес-логика сервиса
│   ├── shortener.py      # Генерация slug
│   ├── schemas.py        # Pydantic схемы (валидация)
│   ├── exceptions.py     # Кастомные исключения
│   ├── config.py         # Конфигурация через pydantic-settings
│   ├── rate_limiter.py   # Rate limiting настройка
│   ├── logging_config.py # Настройка логирования
│   └── database/
│       ├── __init__.py   # Database package
│       ├── models.py     # SQLAlchemy модели (ShortURL, Click)
│       ├── db.py         # Настройки подключения к БД
│       └── crud.py       # Операции с БД
├── tests/
│   ├── test_api.py       # API тесты (28 тестов)
│   ├── test_service.py   # Service тесты (24 теста)
│   └── conftest.py       # Фикстуры pytest
├── alembic/
│   ├── versions/         # Миграции БД
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Template для миграций
├── .github/
│   └── workflows/
│       └── ci-cd.yaml    # GitHub Actions workflow
├── .pre-commit-config.yaml  # Pre-commit хуки
├── .env.example          # Пример переменных окружения
├── alembic.ini           # Alembic конфигурация
├── Dockerfile            # Docker образ приложения
├── index.html            # Фронтенд (Soft UI дизайн)
├── docker-compose.yaml   # PostgreSQL контейнер
├── pyproject.toml        # Зависимости проекта
└── README.md             # Документация
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.9+
- uv (рекомендуется) или pip
- Docker & Docker Compose (для БД)

### 1. Клонирование репозитория

```bash
git clone https://github.com/GloryWater/url_shortener.git
cd url_shortener
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения и установка зависимостей через uv
uv sync --extra dev

# Или через pip:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте при необходимости:

```bash
cp .env.example .env
```

**Основные переменные:**
- `POSTGRES_HOST`, `POSTGRES_PORT` — хост и порт БД
- `POSTGRES_USER`, `POSTGRES_PASSWORD` — учетные данные БД
- `SQL_ECHO` — логирование SQL-запросов (`true`/`false`)
- `ALLOWED_ORIGINS` — разрешенные CORS origin (через запятую)
- `DEBUG` — режим отладки
- `RATE_LIMIT_PER_MINUTE` — лимит запросов в минуту

### 4. Запуск базы данных (Docker)

```bash
docker-compose up -d
```

База данных будет доступна на `localhost:6432`.

### 5. Применение миграций

```bash
# Применить все миграции
uv run alembic upgrade head
```

### 6. Запуск сервера

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на `http://localhost:8000`

### 7. Открыть фронтенд

Перейдите на `http://localhost:8000` — там уже ждет стильный интерфейс!

---

## 📡 API Endpoints

### API v1 (рекомендуется)

| Метод  | Endpoint              | Описание                          | Тело запроса |
|--------|-----------------------|-----------------------------------|--------------|
| `POST` | `/api/v1/urls`        | Создать короткую ссылку           | `{long_url, custom_slug?, expires_in_days?}` |
| `GET`  | `/api/v1/urls`        | Список всех ссылок (пагинация)    | `?page=1&limit=20` |
| `GET`  | `/api/v1/urls/{slug}` | Получить информацию о ссылке      | — |
| `DELETE` | `/api/v1/urls/{slug}` | Удалить ссылку                  | — |
| `GET`  | `/api/v1/urls/{slug}/stats` | Статистика кликов           | — |

### Legacy endpoints (для обратной совместимости)

| Метод  | Endpoint      | Описание                    |
|--------|---------------|-----------------------------|
| `GET`  | `/`           | Главная страница (фронтенд) |
| `POST` | `/short_url`  | Создать короткую ссылку     |
| `GET`  | `/{slug}`     | Редирект + аналитика        |

### Health Check

| Метод  | Endpoint   | Описание              |
|--------|------------|-----------------------|
| `GET`  | `/health`  | Проверка здоровья API |

---

## 📝 Примеры запросов

### Создание короткой ссылки

```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://github.com/GloryWater/url_shortener"}'
```

**Ответ:**
```json
{
  "data": "aB3xY9",
  "short_url": "http://localhost:8000/aB3xY9",
  "long_url": "https://github.com/GloryWater/url_shortener",
  "custom_slug": false,
  "expires_at": null
}
```

### Создание с кастомным slug

```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "custom_slug": "mylink"}'
```

**Ответ:**
```json
{
  "data": "mylink",
  "short_url": "http://localhost:8000/mylink",
  "long_url": "https://example.com",
  "custom_slug": true,
  "expires_at": null
}
```

### Создание с сроком действия

```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "expires_in_days": 30}'
```

### Получение информации о ссылке

```bash
curl http://localhost:8000/api/v1/urls/aB3xY9
```

**Ответ:**
```json
{
  "slug": "aB3xY9",
  "long_url": "https://github.com/GloryWater/url_shortener",
  "custom_slug": false,
  "expires_at": null,
  "created_at": "2026-02-20T12:00:00Z",
  "updated_at": "2026-02-20T12:00:00Z",
  "click_count": 42
}
```

### Статистика кликов

```bash
curl http://localhost:8000/api/v1/urls/aB3xY9/stats
```

**Ответ:**
```json
{
  "total_clicks": 150,
  "last_click": "2026-02-20T15:30:00Z",
  "unique_ips": 42
}
```

### Список ссылок с пагинацией

```bash
curl "http://localhost:8000/api/v1/urls?page=1&limit=20"
```

### Удаление ссылки

```bash
curl -X DELETE http://localhost:8000/api/v1/urls/aB3xY9
```

**Ответ:**
```json
{
  "success": true,
  "message": "URL successfully deleted"
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "version": "0.2.0",
  "database": "connected"
}
```

---

## 🧪 Запуск тестов

```bash
# Запустить все тесты
uv run pytest

# Запустить с покрытием
uv run pytest --cov=src --cov-report=html

# Запустить конкретный тест
uv run pytest tests/test_api.py -v

# Запустить тесты с выводом медленных тестов
uv run pytest --durations=10
```

> Тесты используют `aiosqlite` (in-memory SQLite) для изоляции и скорости.

---

## 🔍 Миграции БД (Alembic)

```bash
# Создать новую миграцию (auto-generate)
uv run alembic revision --autogenerate -m "Description"

# Создать пустую миграцию
uv run alembic revision -m "Description"

# Применить миграции
uv run alembic upgrade head

# Откатить миграцию
uv run alembic downgrade -1

# Показать текущую ревизию
uv run alembic current

# Показать историю миграций
uv run alembic history
```

---

## 🔒 Rate Limiting

По умолчанию установлены лимиты:
- **60 запросов в минуту** на IP
- **1000 запросов в час** на IP

Для изменения настройте в `.env`:
```env
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=2000
```

---

## 🛡️ Security Headers

Приложение автоматически добавляет security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`
- `Referrer-Policy`
- `Permissions-Policy`

---

## 📊 Логирование

### Development режим
```
2026-02-20 12:00:00 | INFO     | src.main:100 | Request received
```

### Production режим
```json
{
  "timestamp": "2026-02-20T12:00:00.000000",
  "level": "INFO",
  "logger": "src.main",
  "location": "/app/src/main.py:100",
  "message": "Request received"
}
```

Для включения production логирования установите:
```env
ENVIRONMENT=production
```

---

## 📡 Swagger документация

После запуска сервера доступна интерактивная API документация:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🚀 CI/CD

Проект использует **GitHub Actions** для автоматической проверки и деплоя:

| Job | Описание |
|-----|----------|
| 🔍 **Pre-commit** | Запускает все pre-commit хуки |
| 🔍 **Lint** | Ruff + MyPy проверки |
| 🧪 **Tests** | pytest с покрытием |
| 🔒 **Security** | проверка зависимостей через Safety |
| 📦 **Build** | сборка Docker образа (только main branch) |
| 🚀 **Deploy** | деплой на сервер через SSH (только main branch) |

---

## 🎨 Особенности фронтенда

- **Soft UI / Glassmorphism** дизайн
- **Адаптивная верстка** (Flexbox/Grid)
- **Градиентный фон** (лиловый → голубой)
- **Анимации** при загрузке результата
- **Валидация** на клиенте
- **Шрифт Inter** от Google Fonts
- **Темная тема** по умолчанию

---

## ⚙️ Конфигурация

Все настройки находятся в `.env` файле:

```env
# Application
APP_NAME=URL Shortener
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=6432
POSTGRES_DB=postgres
SQL_ECHO=false

# CORS
ALLOWED_ORIGINS=http://localhost:5500,http://localhost:8000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Slug Settings
SLUG_LENGTH=6
SLUG_MAX_ATTEMPTS=5

# Security
SECRET_KEY=change-me-in-production
```

---

## 📝 Changelog

### v2.0 (2026-02-20)

**Новые функции:**
- ✅ pydantic-settings для валидации конфигурации
- ✅ Alembic миграции
- ✅ Rate Limiting (slowapi)
- ✅ Health check endpoint
- ✅ API версионирование (`/api/v1/`)
- ✅ Аналитика переходов (Click модель)
- ✅ Удаление ссылок (DELETE endpoint)
- ✅ Список ссылок с пагинацией
- ✅ Кастомные slug и срок действия
- ✅ Валидация на дубликаты long_url
- ✅ Security headers middleware
- ✅ Глобальные exception handlers
- ✅ Расширенные тесты (52 теста)
- ✅ Структурированное логирование

**Breaking changes:**
- API перемещен на `/api/v1/urls`
- Legacy endpoints `/short_url` и `/{slug}` сохранены

### v1.0 (Initial release)

- Базовый функционал сокращения ссылок
- PostgreSQL + SQLAlchemy
- FastAPI backend
- Vanilla JS frontend

---

## 👤 Автор

**Evgeniy Sytcevich**

Проект создан для демонстрации современных возможностей FastAPI и асинхронного стека Python.

---

<div align="center">

**Made with ❤️ using FastAPI + PostgreSQL + SQLAlchemy 2.0**

[View on GitHub](https://github.com/GloryWater/url_shortener) • [API Docs](http://localhost:8000/docs)

</div>
