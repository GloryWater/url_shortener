from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import engine, new_session
from src.database.models import Base
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError
from src.service import generate_short_url, get_url_by_slug


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session


@app.post("/short_url")
async def generate_slug(
    long_url: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    (long_url)
    try:
        new_slug = await generate_short_url(long_url, session)
    except SlugAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сгенерировать slug",
        )
    return {"data": new_slug}


@app.get("/{slug}")
async def redirect_to_url(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        long_url = await get_url_by_slug(slug, session)
    except NoLongUrlFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ссылка не существует"
        )
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
