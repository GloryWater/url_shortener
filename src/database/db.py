from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    url="postgresql+asyncpg://postgres:postgres@localhost:6432/postgres",
    pool_size=20,
    max_overflow=30,
)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)
