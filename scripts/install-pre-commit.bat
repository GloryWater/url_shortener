@echo off
REM Script for installing pre-commit hooks and project verification

echo ============================================
echo 🔧 Installing pre-commit hooks...
echo ============================================
uv run pre-commit install

echo.
echo ✅ Pre-commit hooks installed!
echo.
echo ============================================
echo 📋 How it works:
echo ============================================
echo Now every 'git commit' command automatically:
echo   1. Ruff check - code error checking
echo   2. Ruff format - code formatting
echo   3. MyPy - type checking (src/ only)
echo.
echo If checks fail, the commit will be rejected!
echo.
echo ============================================
echo 📝 Available commands:
echo ============================================
echo   git commit -m "message"           # Normal commit (with checks)
echo   git commit --no-verify -m "msg"   # Commit without checks (not recommended)
echo.
echo   uv run pre-commit run             # Run checks manually
echo   uv run pre-commit run --all-files # Check all files
echo   uv run pre-commit uninstall       # Uninstall hooks
echo.
echo ============================================
echo 🧪 Running tests:
echo ============================================
echo   uv run pytest                     # Run all tests
echo   uv run pytest --cov=src           # Run tests with coverage
echo   uv run pytest -v                  # Verbose test output
echo.
echo ============================================
echo 🔍 Running linters manually:
echo ============================================
echo   uv run ruff check src tests       # Ruff lint
echo   uv run ruff format src tests      # Ruff format
echo   uv run mypy src                   # MyPy type check
echo.
echo ============================================
