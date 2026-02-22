# 🚀 Полная инструкция по деплою URL Shortener на сервер

Эта инструкция проведет вас через **все шаги** деплоя приложения на чистый сервер (Ubuntu/Debian).

---

## 📋 Требования

- Сервер с Ubuntu 20.04+ или Debian 10+
- root доступ или пользователь с sudo правами
- Домен или статический IP (опционально)

---

## Шаг 1: Подготовка сервера

### 1.1 Подключитесь к серверу

```bash
ssh root@your-server-ip
# или
ssh user@your-server-ip
```

### 1.2 Обновите систему

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Установите Docker

```bash
# Скачайте скрипт установки Docker
curl -fsSL https://get.docker.com -o get-docker.sh

# Запустите установку
sudo sh get-docker.sh

# Добавьте пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Примените изменения группы (или перелогиньтесь)
newgrp docker

# Проверьте установку
docker --version
```

### 1.4 Установите Docker Compose Plugin

```bash
# Для Ubuntu/Debian
sudo apt update
sudo apt install -y docker-compose-plugin

# Проверьте установку
docker compose version
```

### 1.5 Установите Git

```bash
sudo apt install -y git
git --version
```

---

## Шаг 2: Клонирование проекта

### 2.1 Создайте директорию приложения

```bash
mkdir -p ~/url-shortener
cd ~/url-shortener
```

### 2.2 Склонируйте репозиторий

```bash
git clone https://github.com/GloryWater/url_shortener.git .
```

---

## Шаг 3: Настройка окружения

### 3.1 Создайте файл .env

```bash
nano .env
```

### 3.2 Вставьте конфигурацию

**Скопируйте и вставьте этот шаблон:**

```env
# Порт приложения
PORT=8001

# Режим работы (production/development)
ENVIRONMENT=production

# DEBUG должен быть false в production
DEBUG=false

# Секретный ключ для JWT (минимум 32 символа!)
# Сгенерируйте случайную строку:
# openssl rand -base64 32
SECRET_KEY=your-super-secret-key-min-32-characters-here

# Пользователь базы данных
POSTGRES_USER=urlshortener

# Пароль базы данных (минимум 16 символов!)
# Сгенерируйте случайную строку:
# openssl rand -base64 16
POSTGRES_PASSWORD=your-strong-password-here

# Имя базы данных
POSTGRES_DB=urlshortener

# Хост базы данных (в Docker сети)
POSTGRES_HOST=db

# Разрешенные CORS origin (укажите ваш домен)
ALLOWED_ORIGINS=http://localhost:8001,http://your-server-ip:8001

# Время жизни JWT токена в минутах
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3.3 Сохраните файл

В nano:
- Нажмите `Ctrl+O` → `Enter` (сохранить)
- Нажмите `Ctrl+X` (выйти)

### 3.4 Проверьте .env

```bash
cat .env
```

---

## Шаг 4: Запуск приложения

### 4.1 Запустите Docker Compose

```bash
docker compose up -d
```

### 4.2 Дождитесь запуска

```bash
# Проверьте статус контейнеров
docker compose ps

# Все сервисы должны быть в статусе "running"
```

### 4.3 Примените миграции базы данных

```bash
docker compose exec url-shortener uv run alembic upgrade head
```

### 4.4 Проверьте логи

```bash
# Логи API
docker compose logs url-shortener

# Логи worker
docker compose logs worker

# Логи базы данных
docker compose logs db

# Логи Redis
docker compose logs redis
```

---

## Шаг 5: Проверка работы

### 5.1 Проверьте health endpoint

```bash
curl http://localhost:8001/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "database": "connected"
}
```

### 5.2 Откройте в браузере

```
http://your-server-ip:8001
```

Вы должны увидеть веб-интерфейс URL Shortener.

### 5.3 Проверьте API Docs

```
http://your-server-ip:8001/docs
```

---

## Шаг 6: Настройка HTTPS (опционально, но рекомендуется)

### 6.1 Установите Nginx

```bash
sudo apt install -y nginx
```

### 6.2 Создайте конфиг Nginx

```bash
sudo nano /etc/nginx/sites-available/url-shortener
```

**Вставьте конфигурацию:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.3 Включите сайт

```bash
sudo ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6.4 Получите SSL сертификат (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Шаг 7: Управление приложением

### Просмотр логов

```bash
# Все логи в реальном времени
docker compose logs -f

# Только API
docker compose logs -f url-shortener

# Последние 100 строк
docker compose logs --tail=100 url-shortener
```

### Перезапуск

```bash
# Перезапустить все сервисы
docker compose restart

# Перезапустить конкретный сервис
docker compose restart url-shortener
```

### Остановка

```bash
# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (данные будут потеряны!)
docker compose down -v
```

### Обновление

```bash
# Перейдите в директорию
cd ~/url-shortener

# Потяните изменения
git pull origin main

# Пересоберите и перезапустите
docker compose up -d --build

# Примените миграции
docker compose exec url-shortener uv run alembic upgrade head
```

---

## Шаг 8: Резервное копирование базы данных

### Создание бэкапа

```bash
# Создайте директорию для бэкапов
mkdir -p ~/backups

# Создайте дамп
docker compose exec -T db pg_dump -U urlshortener urlshortener > ~/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Проверьте бэкап
ls -lh ~/backups/
```

### Восстановление из бэкапа

```bash
# Восстановите дамп
docker compose exec -T db psql -U urlshortener urlshortener < ~/backups/backup_20260101.sql
```

---

## 🔧 Диагностика проблем

### Контейнер не запускается

```bash
# Проверьте статус
docker compose ps

# Проверьте логи
docker compose logs url-shortener

# Перезапустите
docker compose restart url-shortener
```

### Ошибка подключения к базе данных

```bash
# Проверьте, что БД запущена
docker compose ps db

# Проверьте логи БД
docker compose logs db

# Проверьте переменные окружения
docker compose exec url-shortener env | grep POSTGRES
```

### Worker не работает

```bash
# Проверьте логи worker
docker compose logs worker

# Перезапустите worker
docker compose restart worker
```

### Порт занят

```bash
# Найдите процесс на порту
sudo lsof -i :8001

# Или измените PORT в .env и перезапустите
docker compose down
docker compose up -d
```

### Миграции не применяются

```bash
# Проверьте текущую версию
docker compose exec url-shortener uv run alembic current

# Примените миграции
docker compose exec url-shortener uv run alembic upgrade head
```

---

## 📊 Мониторинг

### Использование ресурсов

```bash
# Проверьте использование ресурсов контейнерами
docker stats
```

### Место на диске

```bash
# Проверьте свободное место
df -h

# Очистите старые Docker образы
docker image prune -af

# Очистите старые контейнеры
docker container prune -f
```

---

## 🔒 Безопасность

### Обязательные действия

1. ✅ Измените `SECRET_KEY` на случайную строку 32+ символов
2. ✅ Измените `POSTGRES_PASSWORD` на сложный пароль 16+ символов
3. ✅ Настройте HTTPS (см. Шаг 6)
4. ✅ Откройте только необходимые порты (80, 443)
5. ✅ Регулярно обновляйте систему: `sudo apt update && sudo apt upgrade -y`

### Настройка фаервола (UFW)

```bash
# Установите UFW
sudo apt install -y ufw

# Разрешите SSH
sudo ufw allow 22/tcp

# Разрешите HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включите фаервол
sudo ufw enable

# Проверьте статус
sudo ufw status
```

---

## 📝 Чек-лист после деплоя

- [ ] Health endpoint возвращает `{"status": "healthy"}`
- [ ] Веб-интерфейс открывается в браузере
- [ ] API Docs доступны по `/docs`
- [ ] Worker запущен (проверьте логи)
- [ ] Миграции применены
- [ ] `.env` содержит безопасные пароли
- [ ] HTTPS настроен (если используется домен)
- [ ] Фаервол настроен
- [ ] Бэкапы настроены

---

## 🆘 Если что-то пошло не так

1. **Проверьте логи:** `docker compose logs -f`
2. **Проверьте статус:** `docker compose ps`
3. **Перезапустите:** `docker compose restart`
4. **Пересоберите:** `docker compose up -d --build`
5. **Откройте Issue:** https://github.com/GloryWater/url_shortener/issues

---

<div align="center">

**Happy Deploying! 🚀**

[GitHub](https://github.com/GloryWater/url_shortener) • [API Docs](http://localhost:8001/docs)

</div>
