from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import get_long_url_by_slug_from_database
from src.exceptions import NoLongUrlFoundError
from src.shortener import generate_short_url as _generate_short_url

# Экспортируем функцию из shortener для обратной совместимости
generate_short_url = _generate_short_url


async def get_url_by_slug(slug: str, session: AsyncSession) -> str:
    """Получает длинную ссылку по slug."""
    long_url = await get_long_url_by_slug_from_database(slug, session)
    if not long_url:
        raise NoLongUrlFoundError("Ссылка не найдена")
    return long_url
