# Alembic Migrations

## Usage

### Create a new migration

```bash
# Auto-generate migration based on model changes
uv run alembic revision --autogenerate -m "Description of changes"

# Create empty migration manually
uv run alembic revision -m "Description of changes"
```

### Apply migrations

```bash
# Upgrade to latest version
uv run alembic upgrade head

# Upgrade to specific revision
uv run alembic upgrade <revision_id>

# Downgrade by one revision
uv run alembic downgrade -1

# Downgrade to specific revision
uv run alembic downgrade <revision_id>
```

### Check migration status

```bash
# Show current revision
uv run alembic current

# Show pending migrations
uv run alembic history
```

### Reset database (WARNING: deletes all data!)

```bash
# Downgrade to base (empty database)
uv run alembic downgrade base

# Then upgrade to head
uv run alembic upgrade head
```

## Notes

- All migrations are stored in `alembic/versions/`
- Migration files are automatically formatted with Ruff
- Each migration runs in a transaction by default
- Use `op.batch_alter_table()` for SQLite compatibility if needed
