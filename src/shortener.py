import string
from secrets import choice
from typing import TYPE_CHECKING, Any, Callable

from src.exceptions import SlugAlreadyExistsError

if TYPE_CHECKING:
    from collections.abc import Coroutine
    from sqlalchemy.ext.asyncio import AsyncSession

ALPHABET: str = string.ascii_letters + string.digits
SLUG_LENGTH = 6
MAX_ATTEMPTS = 5


def generate_random_slug(length: int = SLUG_LENGTH) -> str:
    """Генерирует случайный slug заданной длины."""
    return "".join(choice(ALPHABET) for _ in range(length))


async def generate_short_url(
    long_url: str,
    session: "AsyncSession",
    add_to_db_func: "Callable[[str, str, AsyncSession], Coroutine[Any, Any, None]] | None" = None,
) -> str:
    """
    Генерирует короткую ссылку для заданного URL.

    Пытается создать уникальный slug до MAX_ATTEMPTS раз.
    Если все попытки исчерпаны, выбрасывает SlugAlreadyExistsError.
    """
    from src.database.crud import add_slug_to_database

    if add_to_db_func is None:
        add_to_db_func = add_slug_to_database

    for attempt in range(MAX_ATTEMPTS):
        slug = generate_random_slug()
        try:
            await add_to_db_func(slug, long_url, session)
            return slug
        except SlugAlreadyExistsError as ex:
            if attempt == MAX_ATTEMPTS - 1:
                raise SlugAlreadyExistsError(
                    f"Не удалось создать уникальный slug после {MAX_ATTEMPTS} попыток"
                ) from ex

    # Эта строка никогда не будет достигнута, но нужна для type checker
    raise SlugAlreadyExistsError
