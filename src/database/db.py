import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Конфигурация подключения к БД через переменные окружения
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "6432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_async_engine(
    url=DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)
