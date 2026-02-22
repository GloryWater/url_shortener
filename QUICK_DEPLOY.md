# ⚡ Быстрый Деплой — URL Shortener

## 🚀 Самый простой способ (Docker Compose)

### 1. Подготовка сервера (5 минут)

```bash
# SSH на сервер
ssh user@your-server.com

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER && newgrp docker

# Создание директории
mkdir -p ~/url-shortener && cd ~/url-shortener
```

### 2. Клонирование и настройка (2 минуты)

```bash
# Клонирование
git clone https://github.com/GloryWater/url_shortener.git .

# Создание .env файла
cat > .env << 'EOF'
PORT=8001
ENVIRONMENT=production
SECRET_KEY=$(openssl rand -base64 32)
POSTGRES_USER=urlshortener
POSTGRES_PASSWORD=$(openssl rand -base64 16)
POSTGRES_DB=urlshortener
POSTGRES_HOST=db
ALLOWED_ORIGINS=http://your-server-ip:8001
EOF
```

### 3. Запуск (3 минуты)

```bash
# Запуск всех сервисов
docker-compose up -d

# Применение миграций
docker-compose exec url-shortener uv run alembic upgrade head

# Проверка
docker-compose ps
curl http://localhost:8001/health
```

**Готово!** Приложение доступно по адресу: `http://your-server-ip:8001`

---

## 📦 Команды для управления

```bash
# Просмотр логов
docker-compose logs -f

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Обновление
git pull && docker-compose up -d --build
```

---

## 🔧 Автоматический деплой (CI/CD)

### Настройка за 10 минут

1. **Создайте SSH ключ:**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/github_deploy
   ssh-copy-id -i ~/.ssh/github_deploy.pub user@server.com
   ```

2. **Добавьте секреты в GitHub:**
   - `SERVER_HOST` = ваш IP
   - `SERVER_USERNAME` = пользователь
   - `SSH_PRIVATE_KEY` = содержимое `~/.ssh/github_deploy`

3. **Пуш в main:**
   ```bash
   git push origin main
   ```

Деплой произойдет автоматически! 🎉

---

## 🐛 Если что-то не работает

```bash
# Проверьте логи
docker-compose logs url-shortener

# Проверьте базу данных
docker-compose logs db

# Перезапустите сервисы
docker-compose restart

# Проверьте порты
sudo netstat -tulpn | grep 8001
```

**Полная документация:** [DEPLOY.md](DEPLOY.md)

---

<div align="center">

**Deployed in 5 minutes! 🎯**

</div>
