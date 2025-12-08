# ⚡ FastAPI URL Shortener

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Coverage](https://img.shields.io/badge/Tests-Pytest-green?style=for-the-badge&logo=pytest&logoColor=white)

> Высокопроизводительный сервис сокращения ссылок с современным асинхронным стеком и эстетичным фронтендом.

Проект представляет собой **Fullstack приложение**: мощный Backend на FastAPI и легкий, стильный Frontend (Vanilla JS + CSS Soft UI). Реализована полная контейнеризация базы данных.

---

## 📸 Демонстрация интерфейса

<!-- Сделай скриншот своего красивого сайта, положи в папку assets/ или корень и раскомментируй строку ниже -->
<!-- ![Dashboard Screenshot](screenshot.png) -->
*Интерфейс выполнен в стиле Soft UI / Glassmorphism с акцентом на приятный пользовательский опыт.*

---

## 🛠️ Технический стек

### Backend & Database
*   **Фреймворк:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous)
*   **Сервер:** Uvicorn
*   **База данных:** PostgreSQL 17 (Docker)
*   **ORM:** SQLAlchemy 2.0 (Async Session)
*   **Драйвер:** asyncpg (High-performance PostgreSQL driver)
*   **Миграции:** Alembic (опционально, если используется)

### Quality Assurance (QA)
*   **Тесты:** Pytest + Pytest-Asyncio
*   **Клиент тестов:** HTTPX (для асинхронных запросов к API)
*   **Тестовая БД:** aiosqlite (для быстрых unit-тестов in-memory)

### Frontend
*   **Стиль:** CSS3 Custom Properties, Flexbox/Grid
*   **Логика:** Vanilla JavaScript (Fetch API)
*   **Дизайн:** Адаптивный, Dark/Light mode ready

---

## 🚀 Быстрый старт

### 1. Предварительные требования
*   Python 3.10+
*   Docker & Docker Compose

### 2. Клонирование и установка зависимостей

```bash
git clone https://github.com/GloryWater/url_shortener.git
cd url_shortener

# Создание и активация виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt