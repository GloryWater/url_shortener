import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import engine, new_session
from src.database.models import Base
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError
from src.schemas import ShortenUrlRequest, ShortenUrlResponse
from src.service import generate_short_url, get_url_by_slug


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="URL Shortener API",
    description="Сервис сокращения ссылок с асинхронным backend на FastAPI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session


@app.get("/")
async def read_root() -> FileResponse:
    return FileResponse("index.html")


@app.post("/short_url", response_model=ShortenUrlResponse)
async def generate_slug(
    request: ShortenUrlRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortenUrlResponse:
    try:
        new_slug = await generate_short_url(str(request.long_url), session)
    except SlugAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сгенерировать slug",
        )
    return ShortenUrlResponse(data=new_slug)


@app.get("/{slug}")
async def redirect_to_url(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RedirectResponse:
    try:
        long_url = await get_url_by_slug(slug, session)
    except NoLongUrlFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ссылка не существует"
        )
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
