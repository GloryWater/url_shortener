from pydantic import BaseModel, Field, HttpUrl


class ShortenUrlRequest(BaseModel):
    """Запрос на сокращение URL."""

    long_url: HttpUrl = Field(..., description="Длинная ссылка для сокращения")


class ShortenUrlResponse(BaseModel):
    """Ответ с сокращенной ссылкой."""

    data: str = Field(..., description="Сокращенный slug")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    detail: str = Field(..., description="Описание ошибки")
