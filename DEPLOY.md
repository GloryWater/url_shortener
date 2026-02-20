# 🚀 Развертывание на сервере (One-Click Deploy)

После настройки CI/CD, развертывание происходит **автоматически** при каждом пуше в ветку `main`.

---

## 📋 Шаг 1: Подготовка сервера

На вашем сервере должен быть установлен **Docker**:

```bash
# Установка Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавить пользователя в группу docker (чтобы не нужен был sudo)
sudo usermod -aG docker $USER
```

> После выполнения команды перелогиньтесь или выполните `newgrp docker`

---

## 🔑 Шаг 2: Настройка GitHub Secrets

Добавьте следующие **секреты** в репозиторий на GitHub:

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret | Описание | Пример |
|--------|----------|--------|
| `SERVER_HOST` | IP-адрес или домен сервера | `192.168.1.100` или `example.com` |
| `SERVER_USERNAME` | Пользователь на сервере | `root` или `deploy` |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ для доступа | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### Как создать SSH-ключ для деплоя

```bash
# Создать новую пару ключей (без passphrase)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy

# Скопировать приватный ключ (для GitHub Secrets)
cat ~/.ssh/github_actions_deploy

# Скопировать публичный ключ на сервер
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub user@your-server
```

> ⚠️ **Важно:** Приватный ключ должен быть в формате OpenSSH (начинается с `-----BEGIN OPENSSH PRIVATE KEY-----`)
>
> 🔒 **Никогда не коммитьте приватные ключи в репозиторий!**

---

## 🎯 Шаг 3: Первый деплой

Просто сделайте пуш в ветку `main`:

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions автоматически:
1. ✅ Запустит тесты и проверки
2. 📦 Соберёт Docker-образ
3. 🚀 Запушит образ в GHCR (GitHub Container Registry)
4. 🎯 Подключится по SSH к серверу и развернёт контейнер

---

## 📊 Мониторинг деплоя

1. Откройте вкладку **Actions** на GitHub
2. Выберите последний workflow run
3. Следите за прогрессом job'а `🚀 Deploy to Server`

---

## 🔍 Проверка после деплоя

Подключитесь к серверу и проверьте:

```bash
# Проверить статус контейнера
docker ps | grep url-shortener

# Посмотреть логи
docker logs url-shortener

# Проверить доступность
curl http://localhost:8000
```

Сервис будет доступен по адресу: `http://your-server-ip:8000`

---

## 🔄 Обновление

Для обновления просто сделайте изменения и запушьте в `main`:

```bash
git push origin main
```

CI/CD автоматически обновит контейнер на сервере.

---

## 🛡️ Опционально: Docker Compose на сервере

Для более удобного управления создайте на сервере `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  url-shortener:
    image: ghcr.io/glorywater/url_shortener/url-shortener:latest
    container_name: url-shortener
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=postgres
      - PORT=8001
    depends_on:
      - db

  db:
    image: postgres:17
    container_name: url-shortener-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Тогда в workflow замените шаг `Run new container` на:

```bash
docker-compose pull
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Ошибка "unauthorized: authentication required"

Убедитесь, что GitHub Token имеет доступ к GHCR. В workflow используется `${{ secrets.GITHUB_TOKEN }}`.

### Ошибка SSH подключения

Проверьте:
- Правильность `SERVER_HOST` и `SERVER_USERNAME`
- Что публичный ключ добавлен в `~/.ssh/authorized_keys` на сервере
- Что SSH-агент разрешает подключение (порт 22 открыт)

### Контейнер не запускается

Проверьте логи:
```bash
docker logs url-shortener
```

Убедитесь, что порт 8000 не занят:
```bash
sudo lsof -i :8000
```

---

## 📝 Changelog деплоя

| Версия | Изменения |
|--------|-----------|
| 1.0 | Initial deploy workflow с SSH |

---

<div align="center">

**Deploy & Forget! 🚀**

</div>
