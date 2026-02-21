# Pre-commit Hooks

## 🚀 Installation

### Windows
```bash
# Run installation script
.\scripts\install-pre-commit.bat
```

### Linux/macOS
```bash
# Make script executable
chmod +x scripts/install-pre-commit.sh

# Run installation
./scripts/install-pre-commit.sh
```

### Manual installation
```bash
uv run pre-commit install
```

---

## 📋 How it Works

After installing pre-commit hooks, **every `git commit` command** automatically runs the following checks:

1. ✅ **Ruff check** - code error checking
2. ✅ **Ruff format** - code formatting
3. ✅ **MyPy** - type checking (only `src/`)

If **any check fails**, the commit is **blocked** and you see an error.

---

## 🔧 Usage Examples

### Normal commit (with checks)
```bash
git add .
git commit -m "Add new feature"
```

If code doesn't pass checks:
```
ruff.....................................................................Failed
- hook id: ruff
- files were modified by this hook

Found 2 errors (2 fixed, 0 remaining).
```

Ruff will automatically fix the errors. Please run `git commit` again.

### Commit without checks (not recommended!)
```bash
git commit --no-verify -m "Hotfix"
```

⚠️ **Use only in emergency cases!**

---

## 📝 Manual Check Execution

### Check all files
```bash
uv run pre-commit run --all-files
```

### Check only modified files
```bash
uv run pre-commit run
```

### Uninstall pre-commit hooks
```bash
uv run pre-commit uninstall
```

---

## 🧪 Running Tests

Pre-commit **does not run tests automatically** on each commit due to performance considerations.

To run tests, use:

```bash
# All tests
uv run pytest

# Tests with coverage
uv run pytest --cov=src --cov-fail-under=80

# Verbose output
uv run pytest -v
```

---

## 🛠️ Configuration

Configuration is in `.pre-commit-config.yaml`.

### Excluding files from checks

Add at the beginning of the file to exclude:
```python
# flake8: noqa
```

Or add pattern to `.pre-commit-config.yaml`:
```yaml
- id: mypy
  exclude: ^tests/
```

---

## ⚠️ Troubleshooting

### "pre-commit: command not found"
Install pre-commit:
```bash
uv pip install pre-commit
```

### MyPy error: 'alembic.op' has no attribute
This is an error in alembic files. Add:
```python
from alembic import op  # type: ignore[attr-defined]
```

### Files modified by pre-commit hooks
Ruff automatically formats code. After the first commit:
1. Run `git add .`
2. Run `git commit` again

---

## 📚 Useful Links

- [Pre-commit documentation](https://pre-commit.com/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [MyPy documentation](https://mypy.readthedocs.io/)
