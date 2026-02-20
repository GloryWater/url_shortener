#!/bin/bash
# Скрипт установки pre-commit хуков и проверки проекта

set -e

echo "🔧 Установка pre-commit хуков..."
uv run pre-commit install

echo ""
echo "✅ Pre-commit хуки установлены!"
echo ""
echo "📋 Доступные команды:"
echo "  pre-commit run                    # Запустить проверки на закоммиченных файлах"
echo "  pre-commit run --all-files        # Запустить проверки на всех файлах"
echo "  pre-commit uninstall              # Удалить pre-commit хуки"
echo ""
echo "🧪 Запуск тестов:"
echo "  uv run pytest                     # Запустить все тесты"
echo "  uv run pytest --cov=src           # Запустить тесты с покрытием"
echo "  uv run pytest -v                  # Запустить тесты с подробным выводом"
echo ""
echo "🔍 Запуск линтеров:"
echo "  uv run ruff check src tests       # Ruff lint"
echo "  uv run ruff format src tests      # Ruff format"
echo "  uv run mypy src tests             # MyPy type check"
