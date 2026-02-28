# ⚡ FastAPI URL Shortener (v3.0)

High-performance SaaS URL shortening service with caching, asynchronous analytics, authentication, and an elegant frontend.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Tests](https://img.shields.io/github/actions/workflow/status/GloryWater/url_shortener/ci.yaml?branch=main&style=for-the-badge&logo=pytest)
![Coverage](https://img.shields.io/codecov/c/github/GloryWater/url_shortener?style=for-the-badge&logo=codecov)
![CI](https://img.shields.io/github/actions/workflow/status/GloryWater/url_shortener/ci.yaml?branch=main&style=for-the-badge&logo=github-actions)
![CD](https://img.shields.io/github/actions/workflow/status/GloryWater/url_shortener/cd.yaml?branch=main&style=for-the-badge&logo=github-actions&label=deploy)

---

## 🌟 Features v3.0

### New Features
- **🔐 User Authentication** - JWT tokens, registration, login
- **⚡ Redis Caching** - Cache-aside pattern for redirects <50ms
- **📬 Asynchronous Analytics** - ARQ queue for background click processing
- **🌍 GeoIP Enrichment** - Country/city detection by IP
- **📊 Prometheus Metrics** - Performance monitoring
- **🧹 Auto-cleanup** - CRON job for removing expired URLs
- **🔒 Graceful Degradation** - Operation during Redis/queue failures

### Architecture Improvements
- **Stateless API** - Horizontal scaling
- **Distributed Locks** - Protection against cache stampede
- **Event-driven Analytics** - Complete decoupling of redirect and analytics

---

## 🛠️ Technology Stack

| Category        | Technologies                                    |
|-----------------|-------------------------------------------------|
| **Backend**     | FastAPI, Uvicorn                                |
| **Database**    | PostgreSQL 17, SQLAlchemy 2.0, asyncpg, Alembic |
| **Cache**       | Redis 7, redis.asyncio                          |
| **Queue**       | ARQ (Redis-based)                               |
| **Auth**        | JWT (PyJWT), passlib[bcrypt]                    |
| **Config**      | pydantic-settings                               |
| **Testing**     | pytest, pytest-asyncio, pytest-cov, httpx       |
| **Frontend**    | Vanilla JavaScript, CSS3 with Soft UI design              |
| **DevOps**      | Docker, Docker Compose, GitHub Actions          |
| **Security**    | slowapi (rate limiting), security headers       |
| **Logging**     | python-json-logger                              |
| **Monitoring**  | prometheus-fastapi-instrumentator               |
| **Analytics**   | user-agents, geoip2                             |

---

## 📦 Project Structure

```
url_shortener/
├── src/
│   ├── main.py                   # API entry point (FastAPI app)
│   ├── service.py                # Service business logic
│   ├── shortener.py              # Slug generation
│   ├── schemas.py                # Pydantic schemas (validation)
│   ├── exceptions.py             # Custom exceptions
│   ├── config.py                 # Configuration via pydantic-settings
│   ├── rate_limiter.py           # Rate limiting configuration
│   ├── logging_config.py         # Logging configuration
│   ├── worker.py                 # ARQ worker for background tasks
│   ├── auth/
│   │   ├── __init__.py           # Auth package
│   │   ├── router.py             # Auth endpoints
│   │   ├── schemas.py            # Auth schemas
│   │   ├── crud.py               # Auth CRUD operations
│   │   ├── jwt.py                # JWT utilities
│   │   └── dependencies.py       # Auth dependencies
│   ├── cache/
│   │   ├── __init__.py           # Cache package
│   │   └── redis_client.py       # Redis client and caching
│   └── database/
│       ├── __init__.py           # Database package
│       ├── models.py             # SQLAlchemy models (User, ShortURL, Click)
│       ├── db.py                 # Database connection settings
│       └── crud.py               # Database operations
├── tests/
│   ├── test_api.py               # API tests
│   ├── test_service.py           # Service tests
│   ├── test_auth.py              # Auth tests
│   ├── test_cache.py             # Cache tests
│   └── conftest.py               # pytest fixtures
├── alembic/
│   ├── versions/                 # Database migrations
│   ├── env.py                    # Alembic environment
│   └── script.py.mako            # Template for migrations
├── .github/
│   ├── workflows/
│   │   ├── ci.yaml               # CI: tests, linting, security
│   │   ├── cd.yaml               # CD: build & deploy
│   │   ├── manual-deploy.yaml    # Manual deployment
│   │   └── release.yaml          # Release workflow
│   └── ENV_TEMPLATE.md           # Environment variables template
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .env.example                  # Example environment variables
├── alembic.ini                   # Alembic configuration
├── docker-compose.yaml           # PostgreSQL + Redis containers
├── Dockerfile                    # Application Docker image
├── index.html                    # Frontend (Soft UI design)
├── pyproject.toml                # Project dependencies
└── README.md                     # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- uv (recommended) or pip
- Docker & Docker Compose (for database and Redis)

### 1. Clone the Repository

```bash
git clone https://github.com/GloryWater/url_shortener.git
cd url_shortener
```

### 2. Install Dependencies

```bash
# Create virtual environment and install dependencies via uv
uv sync --extra dev

# Or via pip:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

**New v3.0 variables:**
- `REDIS_HOST`, `REDIS_PORT` — Redis connection
- `REDIS_TTL` — Cache TTL (default 24 hours)
- `SECRET_KEY` — Key for JWT signing
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` — Token lifetime
- `ENVIRONMENT` — development/production

### 4. Start Database and Redis (Docker)

```bash
docker-compose up -d
```

Services:
- PostgreSQL on `localhost:6432`
- Redis on `localhost:6379`

### 5. Apply Migrations

```bash
# Apply all migrations (including the new one for users)
uv run alembic upgrade head
```

### 6. Start Server and Worker

```bash
# Terminal 1: Start API server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Start background worker
arq src.worker.WorkerSettings
```

### 7. Open Frontend

Go to `http://localhost:8001` — a stylish web interface is included!

---

## 📡 API Endpoints

### Authentication v1

| Method | Endpoint              | Description                       | Auth |
|--------|-----------------------|-----------------------------------|------|
| `POST` | `/api/v1/auth/register` | User registration                | ❌ |
| `POST` | `/api/v1/auth/login`    | Login and get JWT token          | ❌ |
| `GET`  | `/api/v1/auth/me`       | Current user information         | ✅ |

### API v1 (URLs)

| Method | Endpoint              | Description                       | Auth |
|--------|-----------------------|-----------------------------------|------|
| `POST` | `/api/v1/urls`        | Create short URL                  | ❌ |
| `GET`  | `/api/v1/urls`        | List all URLs (pagination)        | ❌ |
| `GET`  | `/api/v1/urls/{slug}` | Get URL information               | ❌ |
| `DELETE` | `/api/v1/urls/{slug}` | Delete URL                      | ✅ |
| `GET`  | `/api/v1/urls/{slug}/stats` | Click statistics             | ❌ |

### Legacy Endpoints (for backward compatibility)

| Method | Endpoint      | Description                     | Auth |
|--------|---------------|---------------------------------|------|
| `GET`  | `/`           | Main page (frontend)            | ❌ |
| `POST` | `/short_url`  | Create short URL                | ❌ |
| `GET`  | `/{slug}`     | Redirect + analytics            | ❌ |

### Health Check & Metrics

| Method | Endpoint   | Description             |
|--------|------------|-------------------------|
| `GET`  | `/health`  | API health check        |
| `GET`  | `/metrics` | Prometheus metrics      |

---

## 📝 Request Examples

### User Registration

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false
}
```

### Login and Get JWT Token

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User Information

```bash
curl http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Create Short URL

```bash
curl -X POST http://localhost:8001/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://github.com/GloryWater/url_shortener"}'
```

**Response:**
```json
{
  "data": "aB3xY9",
  "short_url": "http://localhost:8001/aB3xY9",
  "long_url": "https://github.com/GloryWater/url_shortener",
  "custom_slug": false,
  "expires_at": null
}
```

### Create with Custom Slug

```bash
curl -X POST http://localhost:8001/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "custom_slug": "mylink"}'
```

**Response:**
```json
{
  "data": "mylink",
  "short_url": "http://localhost:8001/mylink",
  "long_url": "https://example.com",
  "custom_slug": true,
  "expires_at": null
}
```

### Create with Expiration

```bash
curl -X POST http://localhost:8001/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com", "expires_in_days": 30}'
```

### Get URL Information

```bash
curl http://localhost:8001/api/v1/urls/aB3xY9
```

**Response:**
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

### Click Statistics

```bash
curl http://localhost:8001/api/v1/urls/aB3xY9/stats
```

**Response:**
```json
{
  "total_clicks": 150,
  "last_click": "2026-02-20T15:30:00Z",
  "unique_ips": 42
}
```

### List URLs with Pagination

```bash
curl "http://localhost:8001/api/v1/urls?page=1&limit=20"
```

### Delete URL

```bash
curl -X DELETE http://localhost:8001/api/v1/urls/aB3xY9
```

**Response:**
```json
{
  "success": true,
  "message": "URL successfully deleted"
}
```

### Health Check

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "database": "connected"
}
```

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_api.py -v

# Run tests with slow test output
uv run pytest --durations=10
```

> Tests use `aiosqlite` (in-memory SQLite) for isolation and speed. Production uses PostgreSQL.

---

## 🔍 Database Migrations (Alembic)

```bash
# Create new migration (auto-generate)
uv run alembic revision --autogenerate -m "Description"

# Create empty migration
uv run alembic revision -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# Show current revision
uv run alembic current

# Show migration history
uv run alembic history
```

---

## 🔒 Rate Limiting

Default limits are set:
- **60 requests per minute** per IP
- **1000 requests per hour** per IP

To change, configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=2000
```

---

## 🛡️ Security Headers

The application automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`
- `Referrer-Policy`
- `Permissions-Policy`

---

## 📊 Logging

### Development Mode
```
2026-02-20 12:00:00 | INFO     | src.main:100 | Request received
```

### Production Mode
```json
{
  "timestamp": "2026-02-20T12:00:00.000000",
  "level": "INFO",
  "logger": "src.main",
  "location": "/app/src/main.py:100",
  "message": "Request received"
}
```

To enable production logging, set:
```env
ENVIRONMENT=production
```

---

## 📡 Swagger Documentation

After starting the server, interactive API documentation is available:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

---

## 🚀 CI/CD

> 📖 **Полная документация:** См. [`CI_CD.md`](CI_CD.md) и [`.github/workflows/`](.github/workflows/)

Проект использует **GitHub Actions** для автоматических проверок и деплоя:

### Workflow файлы

| Workflow | Описание | Триггеры |
|----------|----------|----------|
| **CI** ([`ci.yaml`](.github/workflows/ci.yaml)) | Тесты, линтеры, безопасность | Push в main/develop, PR |
| **CD** ([`cd.yaml`](.github/workflows/cd.yaml)) | Сборка и деплой на сервер | Push в main |
| **Manual Deploy** ([`manual-deploy.yaml`](.github/workflows/manual-deploy.yaml)) | Ручной деплой в любую среду | Workflow dispatch |
| **Release** ([`release.yaml`](.github/workflows/release.yaml)) | Создание релизов с тегами | Push тега v* |

### Статусы

| Job | Описание |
|-----|-------------|
| 🔍 **Lint** | Ruff linter + formatter |
| 🔍 **Type Check** | MyPy strict mode |
| 🧪 **Tests** | pytest с coverage (70%+) |
| 🔒 **Security** | pip-audit + Bandit |
| 🐳 **Docker** | Проверка сборки образа |
| 📦 **Build & Push** | Сборка и push в GHCR |
| 🚀 **Deploy** | Деплой на сервер via SSH |

---

## 🎨 Frontend Features

- **Soft UI / Glassmorphism** design
- **Responsive layout** (Flexbox/Grid)
- **Gradient background** (lilac → blue)
- **Animations** on result loading
- **Validation** on client side
- **Inter font** from Google Fonts
- **Dark theme** by default

---

## ⚙️ Configuration

All settings are in the `.env` file:

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
ALLOWED_ORIGINS=http://localhost:5500,http://localhost:8001

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

**New Features:**
- ✅ pydantic-settings for configuration validation
- ✅ Alembic migrations
- ✅ Rate Limiting (slowapi)
- ✅ Health check endpoint
- ✅ API versioning (`/api/v1/`)
- ✅ Click analytics (Click model)
- ✅ URL deletion (DELETE endpoint)
- ✅ URL list with pagination
- ✅ Custom slug and expiration
- ✅ Duplicate long_url validation
- ✅ Security headers middleware
- ✅ Global exception handlers
- ✅ Extended tests (52 tests)
- ✅ Structured logging

**Breaking Changes:**
- API moved to `/api/v1/urls`
- Legacy endpoints `/short_url` and `/{slug}` preserved

### v1.0 (Initial release)

- Basic URL shortening functionality
- PostgreSQL + SQLAlchemy
- FastAPI backend
- Vanilla JS frontend

---

## 👤 Author

**Evgeniy Sytcevich**

Project created to demonstrate modern FastAPI capabilities and Python async stack.

---

<div align="center">

**Made with ❤️ using FastAPI + PostgreSQL + SQLAlchemy 2.0**

[View on GitHub](https://github.com/GloryWater/url_shortener) • [API Docs](http://localhost:8001/docs)

</div>
