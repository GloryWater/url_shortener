# GitHub Actions Environment Variables Template
# Скопируйте этот файл и используйте как шаблон для настройки environments

# ===========================================
# Production Environment
# ===========================================
# Settings → Environments → production → Environment variables

# SERVER_HOST=your-production-server.com
# SERVER_USERNAME=deploy
# SERVER_URL=https://yourdomain.com
# DEPLOY_PATH=~/url-shortener

# ===========================================
# Staging Environment (optional)
# ===========================================
# Settings → Environments → staging → Environment variables

# SERVER_HOST=staging.yourdomain.com
# SERVER_USERNAME=deploy
# SERVER_URL=https://staging.yourdomain.com
# DEPLOY_PATH=~/url-shortener-staging

# ===========================================
# Development Environment (optional)
# ===========================================
# Settings → Environments → development → Environment variables

# SERVER_HOST=dev.yourdomain.com
# SERVER_USERNAME=deploy
# SERVER_URL=https://dev.yourdomain.com
# DEPLOY_PATH=~/url-shortener-dev

# ===========================================
# Repository Secrets (required for all environments)
# ===========================================
# Settings → Secrets and variables → Actions → New repository secret

# SSH_PRIVATE_KEY=(your SSH private key for deployment)
#
# SERVER_HOST=your-server.com
# SERVER_USERNAME=deploy

# ===========================================
# Optional Secrets
# ===========================================

# CODECOV_TOKEN=your-codecov-token (for coverage reports)
