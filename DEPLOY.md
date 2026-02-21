# 🚀 Server Deployment (Automated CI/CD)

After setting up CI/CD, deployment happens **automatically** with every push to the `main` branch.

---

## 📋 Step 1: Server Preparation

Your server must have **Docker** installed:

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (so sudo is not needed)
sudo usermod -aG docker $USER
```

> After running the command, relogin or run `newgrp docker`

---

## 🔑 Step 2: Configure GitHub Secrets

Add the following **secrets** to your GitHub repository:

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret | Description | Example |
|--------|----------|--------|
| `SERVER_HOST` | Server IP address or domain | `192.168.1.100` or `example.com` |
| `SERVER_USERNAME` | Server username | `root` or `deploy` |
| `SSH_PRIVATE_KEY` | Private SSH key for access | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### How to Create SSH Key for Deployment

```bash
# Create new key pair (without passphrase)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy

# Copy private key (for GitHub Secrets)
cat ~/.ssh/github_actions_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub user@your-server
```

> ⚠️ **Important:** Private key must be in OpenSSH format (starts with `-----BEGIN OPENSSH PRIVATE KEY-----`)
>
> 🔒 **Never commit private keys to the repository!**

---

## 🎯 Step 3: First Deployment

Simply push to the `main` branch:

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will automatically:
1. ✅ Run tests and checks
2. 📦 Build Docker image
3. 🚀 Push image to GHCR (GitHub Container Registry)
4. 🎯 Connect to server via SSH and deploy container

---

## 📊 Monitor Deployment

1. Open the **Actions** tab on GitHub
2. Select the latest workflow run
3. Follow the progress of the `🚀 Deploy to Server` job

---

## 🔍 Post-Deployment Verification

Connect to the server and verify:

```bash
# Check container status
docker ps | grep url-shortener

# View logs
docker logs url-shortener

# Check availability
curl http://localhost:8000
```

The service will be available at: `http://your-server-ip:8000`

---

## 🔄 Updates

To update, simply make changes and push to `main`:

```bash
git push origin main
```

CI/CD will automatically update the container on the server.

---

## 🛡️ Optional: Docker Compose on Server

For easier management, you can create a `docker-compose.yaml` file on the server:

```yaml
version: '3.8'

services:
  url-shortener:
    image: ghcr.io/glorywater/url-shortener/url-shortener:latest
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

Then in the workflow, replace the `Run new container` step with:

```bash
docker-compose pull
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Error "unauthorized: authentication required"

Make sure the GitHub token has access to GHCR. The workflow uses `${{ secrets.GITHUB_TOKEN }}`.

### SSH Connection Error

Check:
- Correctness of `SERVER_HOST` and `SERVER_USERNAME`
- That the public key is added to `~/.ssh/authorized_keys` on the server
- That SSH agent allows connection (port 22 is open)

### Container Not Starting

Check logs:
```bash
docker logs url-shortener
```

Make sure port 8000 is not busy:
```bash
sudo lsof -i :8000
```

---

## 📝 Deployment Changelog

| Version | Changes |
|--------|---------|
| 1.0 | Initial deploy workflow with SSH |

---

<div align="center">

**Deploy & Forget! 🚀**

</div>
