# 🚀 URL Shortener — Полное Руководство по Деплою

Это руководство описывает **все способы** развертывания приложения — от локального тестирования до production на сервере.

---

## 📋 Оглавление

1. [Быстрый старт (локально)](#-быстрый-старт-локально)
2. [Деплой через Docker Compose (рекомендуется)](#-деплой-через-docker-compose-рекомендуется)
3. [Автоматический деплой через CI/CD](#-автоматический-деплой-через-cicd)
4. [Ручной деплой на сервер](#-ручной-деплой-на-сервер)
5. [Настройка окружения](#-настройка-окружения)
6. [Диагностика проблем](#-диагностика-проблем)

---

## 🏃 Быстрый старт (локально)

### Требования
- Python 3.9+ (рекомендуется 3.12)
- uv (менеджер пакетов)
- Docker & Docker Compose

### Шаг 1: Установка зависимостей

```bash
# Клонируйте репозиторий
git clone https://github.com/GloryWater/url_shortener.git
cd url_shortener

# Установите uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Создайте виртуальное окружение и установите зависимости
uv sync --extra dev
```

### Шаг 2: Настройка окружения

```bash
# Скопируйте пример конфигурации
cp .env.example .env
```

**Минимальная конфигурация для локальной разработки:**

```env
# .env
PORT=8001
SECRET_KEY=my-secret-key-change-in-production
ENVIRONMENT=development
```

### Шаг 3: Запуск базы данных и Redis

```bash
docker-compose up -d db redis
```

### Шаг 4: Применение миграций

```bash
uv run alembic upgrade head
```

### Шаг 5: Запуск приложения

**Терминал 1 — API сервер:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

**Терминал 2 — Worker (фоновые задачи):**
```bash
arq src.worker.WorkerSettings
```

### Проверка

Откройте в браузере:
- **Frontend:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health

---

## 🐳 Деплой через Docker Compose (рекомендуется)

Этот способ подходит для **production** на одном сервере.

### Шаг 1: Подготовка сервера

```bash
# Подключитесь к серверу
ssh user@your-server.com

# Установите Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Примените изменения группы
newgrp docker

# Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверьте установку
docker --version
docker-compose --version
```

### Шаг 2: Создание директории приложения

```bash
# Создайте директорию
mkdir -p ~/url-shortener
cd ~/url-shortener
```

### Шаг 3: Создание файлов конфигурации

**Создайте `.env` файл:**

```bash
nano .env
```

**Содержимое `.env`:**
```env
# ===========================================
# Production Configuration
# ===========================================

# Application
PORT=8001
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-min-32-chars-here

# Database
POSTGRES_USER=urlshortener
POSTGRES_PASSWORD=strong-password-here-min-16-chars
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=urlshortener

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_TTL=86400

# CORS (укажите ваш домен)
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:8001

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Security
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ **Важно:** Замените значения на свои! Особенно `SECRET_KEY` и пароли.

### Шаг 4: Создание Docker Compose файла

**Создайте `docker-compose.prod.yaml`:**

```bash
nano docker-compose.prod.yaml
```

**Содержимое `docker-compose.prod.yaml`:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:17
    container_name: url-shortener-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: urlshortener
      POSTGRES_USER: urlshortener
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U urlshortener"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - url-shortener-network

  redis:
    image: redis:7-alpine
    container_name: url-shortener-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - url-shortener-network

  url-shortener:
    build: .
    container_name: url-shortener-api
    restart: unless-stopped
    ports:
      - "${PORT:-8001}:8001"
    environment:
      - PORT=8001
      - ENVIRONMENT=${ENVIRONMENT}
      - SECRET_KEY=${SECRET_KEY}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - JWT_ACCESS_TOKEN_EXPIRE_MINUTES=${JWT_ACCESS_TOKEN_EXPIRE_MINUTES}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - url-shortener-network

  worker:
    build: .
    container_name: url-shortener-worker
    restart: unless-stopped
    command: arq src.worker.WorkerSettings
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - SECRET_KEY=${SECRET_KEY}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - url-shortener-network

volumes:
  postgres_data:
  redis_data:

networks:
  url-shortener-network:
    driver: bridge
```

### Шаг 5: Копирование файлов проекта

```bash
# Скопируйте файлы проекта на сервер
# С локальной машины:
scp -r * user@your-server:~/url-shortener/
```

Или клонируйте репозиторий прямо на сервере:

```bash
git clone https://github.com/GloryWater/url_shortener.git .
```

### Шаг 6: Запуск приложения

```bash
# Постройте и запустите все сервисы
docker-compose -f docker-compose.prod.yaml up -d --build

# Проверьте статус
docker-compose -f docker-compose.prod.yaml ps
```

### Шаг 7: Применение миграций

```bash
# Примените миграции базы данных
docker-compose -f docker-compose.prod.yaml exec url-shortener uv run alembic upgrade head
```

### Проверка

```bash
# Проверьте логи
docker-compose -f docker-compose.prod.yaml logs -f url-shortener

# Проверьте доступность
curl http://localhost:8001/health
```

Приложение доступно по адресу: `http://your-server-ip:8001`

---

## 🔄 Автоматический деплой через CI/CD

GitHub Actions автоматически развернет приложение при пуше в `main`.

### Как это работает

Проект использует **два отдельных workflow**:

1. **CI Tests** (`.github/workflows/ci-tests.yaml`) — запускает тесты и проверки
2. **CD Deploy** (`.github/workflows/cd-deploy.yaml`) — строит Docker image и разворачивает на сервере

### Шаг 1: Настройка SSH ключа

**На локальной машине:**

```bash
# Создайте SSH ключ для деплоя
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Скопируйте публичный ключ на сервер
ssh-copy-id -i ~/.ssh/github_deploy.pub user@your-server.com

# Проверьте подключение
ssh -i ~/.ssh/github_deploy user@your-server.com
```

### Шаг 2: Добавление секретов в GitHub

Перейдите в: `GitHub Repository` → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Секрет | Описание | Пример |
|--------|----------|--------|
| `SERVER_HOST` | IP или домен сервера | `192.168.1.100` или `example.com` |
| `SERVER_USERNAME` | Пользователь на сервере | `root` или `deploy` |
| `SSH_PRIVATE_KEY` | Приватный SSH ключ | Содержимое `~/.ssh/github_deploy` |

**Как получить приватный ключ:**

```bash
cat ~/.ssh/github_deploy
```

Скопируйте всё содержимое (включая `-----BEGIN OPENSSH PRIVATE KEY-----` и `-----END...`) и вставьте в секрет GitHub.

### Шаг 3: Деплой

Просто сделайте пуш в `main` ветку:

```bash
git add .
git commit -m "Deploy new version"
git push origin main
```

**Что произойдет:**

1. ✅ Запустятся тесты и проверки (pre-commit, ruff, mypy, pytest)
2. ✅ Соберется Docker image
3. ✅ Image будет запушен в GHCR (GitHub Container Registry)
4. ✅ GitHub Actions подключится к серверу по SSH
5. ✅ Сервер скачает новый image и перезапустит контейнеры
6. ✅ Применятся миграции базы данных

### Мониторинг деплоя

1. Откройте вкладку **Actions** на GitHub
2. Выберите последний запуск workflow
3. Следите за прогрессом в реальном времени

---

## 🖥️ Ручной деплой на сервер

Если вы предпочитаете контролировать каждый шаг.

### Шаг 1: Подготовка

```bash
# Подключитесь к серверу
ssh user@your-server.com

# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите зависимости
sudo apt install -y docker.io docker-compose git curl
```

### Шаг 2: Клонирование проекта

```bash
cd ~
git clone https://github.com/GloryWater/url_shortener.git
cd url-shortener
```

### Шаг 3: Настройка окружения

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте под production
nano .env
```

### Шаг 4: Запуск

```bash
# Постройте и запустите
docker-compose up -d

# Примените миграции
docker-compose exec url-shortener uv run alembic upgrade head

# Проверьте статус
docker-compose ps
```

---

## ⚙️ Настройка окружения

### Переменные окружения

| Переменная | Описание | По умолчанию | Production значение |
|------------|----------|--------------|---------------------|
| `PORT` | Порт приложения | `8001` | `8001` |
| `ENVIRONMENT` | Режим работы | `development` | `production` |
| `DEBUG` | Режим отладки | `false` | `false` |
| `SECRET_KEY` | Ключ для JWT | `change-me...` | **Минимум 32 символа** |
| `POSTGRES_USER` | Пользователь БД | `postgres` | Уникальное имя |
| `POSTGRES_PASSWORD` | Пароль БД | `postgres` | **Минимум 16 символов** |
| `POSTGRES_HOST` | Хост БД | `localhost` | `db` (в Docker) |
| `POSTGRES_PORT` | Порт БД | `6432` | `5432` (в Docker) |
| `POSTGRES_DB` | Имя БД | `postgres` | `urlshortener` |
| `REDIS_HOST` | Хост Redis | `localhost` | `redis` (в Docker) |
| `REDIS_PORT` | Порт Redis | `6379` | `6379` |
| `ALLOWED_ORIGINS` | CORS origin | `http://localhost:5500` | `https://yourdomain.com` |
| `RATE_LIMIT_PER_MINUTE` | Лимит запросов/мин | `60` | `60` |
| `RATE_LIMIT_PER_HOUR` | Лимит запросов/час | `1000` | `1000` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `30` | `30` |

### Генерация SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32

# Base64
openssl rand -base64 32
```

---

## 🐛 Диагностика проблем

### Контейнер не запускается

```bash
# Проверьте логи
docker-compose logs url-shortener

# Проверьте статус
docker-compose ps

# Перезапустите
docker-compose restart url-shortener
```

### Ошибка "Cannot add middleware after an application has started"

**Проблема:** Instrumentator инициализируется внутри lifespan контекста.

**Решение:** Убедитесь, что вы используете последнюю версию кода. Эта ошибка была исправлена в версии 0.3.1.

### Ошибка "cron_jobs, must be instances of CronJob"

**Проблема:** Неправильный формат cron_jobs в worker.py.

**Решение:** Убедитесь, что вы используете последнюю версию кода. Эта ошибка была исправлена в версии 0.3.1.

### Ошибка подключения к базе данных

```bash
# Проверьте, что БД запущена
docker-compose ps db

# Проверьте логи БД
docker-compose logs db

# Проверьте переменные окружения
docker-compose exec url-shortener env | grep POSTGRES
```

### Ошибка Redis

```bash
# Проверьте Redis
docker-compose exec redis redis-cli ping

# Должно вернуть: PONG
```

### Миграции не применяются

```bash
# Проверьте текущую версию
docker-compose exec url-shortener uv run alembic current

# Примените заново
docker-compose exec url-shortener uv run alembic upgrade head
```

### Порт занят

```bash
# Найдите процесс на порту
sudo lsof -i :8001

# Или через netstat
sudo netstat -tulpn | grep 8001

# Остановите процесс или измените PORT в .env
```

### Проблемы с CORS

Если браузер блокирует запросы:

```env
# В .env добавьте ваш домен
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:8001
```

### Worker не обрабатывает клики

```bash
# Проверьте логи worker
docker-compose logs worker

# Перезапустите worker
docker-compose restart worker
```

---

## 📊 Мониторинг и обслуживание

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только API
docker-compose logs -f url-shortener

# Только БД
docker-compose logs -f db

# За последние 100 строк
docker-compose logs --tail=100 url-shortener
```

### Резервное копирование базы данных

```bash
# Создать дамп
docker-compose exec db pg_dump -U urlshortener urlshortener > backup_$(date +%Y%m%d).sql

# Восстановить из дампа
docker-compose exec -T db psql -U urlshortener urlshortener < backup_20260101.sql
```

### Обновление приложения

```bash
# Потяните изменения
git pull origin main

# Пересоберите и перезапустите
docker-compose up -d --build

# Примените миграции
docker-compose exec url-shortener uv run alembic upgrade head
```

### Очистка старых образов

```bash
# Удалить неиспользуемые образы
docker image prune -af

# Удалить старые контейнеры
docker container prune -f
```

---

## 🔒 Безопасность

### Обязательные действия для production

1. **Измените SECRET_KEY** на случайную строку 32+ символов
2. **Измените пароль БД** на сложный (16+ символов)
3. **Настройте HTTPS** через reverse proxy (nginx/traefik)
4. **Ограничьте доступ** к портам БД и Redis (не публикуйте наружу)
5. **Регулярно обновляйте** зависимости и образы

### Настройка HTTPS через Nginx

**Установите nginx:**

```bash
sudo apt install -y nginx
```

**Создайте конфиг `/etc/nginx/sites-available/url-shortener`:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Получите SSL сертификат (Let's Encrypt):**

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 📝 Changelog деплоя

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.0 | 2026-02-22 | Полная переработка документации, добавлен Docker Compose |
| 1.0 | 2026-02-20 | Initial deploy workflow |

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте [секцию диагностики](#-диагностика-проблем)
2. Посмотрите логи: `docker-compose logs -f`
3. Откройте [Issue на GitHub](https://github.com/GloryWater/url_shortener/issues)

---

<div align="center">

**Happy Deploying! 🚀**

[GitHub](https://github.com/GloryWater/url_shortener) • [API Docs](http://localhost:8001/docs)

</div>
