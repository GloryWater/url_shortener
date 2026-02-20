from httpx import AsyncClient


async def test_generate_slug(ac: AsyncClient) -> None:
    """Тест создания короткой ссылки."""
    result = await ac.post("/short_url", json={"long_url": "https://my-site.com"})
    assert result.status_code == 200
    data = result.json()
    assert "data" in data
    assert len(data["data"]) == 6


async def test_generate_slug_invalid_url(ac: AsyncClient) -> None:
    """Тест с невалидным URL."""
    result = await ac.post("/short_url", json={"long_url": "not-a-url"})
    assert result.status_code == 422


async def test_redirect_to_url(ac: AsyncClient) -> None:
    """Тест редиректа на оригинальную ссылку."""
    # Сначала создаем ссылку
    create_result = await ac.post(
        "/short_url", json={"long_url": "https://example.com/test"}
    )
    slug = create_result.json()["data"]

    # Проверяем редирект (302 Found)
    response = await ac.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 302
    assert "https://example.com/test" in response.headers["location"]


async def test_redirect_not_found(ac: AsyncClient) -> None:
    """Тест редиректа для несуществующего slug."""
    result = await ac.get("/nonexistent", follow_redirects=False)
    assert result.status_code == 404


async def test_generate_multiple_slugs_unique(ac: AsyncClient) -> None:
    """Тест уникальности сгенерированных slug."""
    slugs: set[str] = set()
    for _ in range(10):
        result = await ac.post(
            "/short_url", json={"long_url": "https://unique-test.com"}
        )
        assert result.status_code == 200
        slugs.add(result.json()["data"])

    # Все slug должны быть уникальными
    assert len(slugs) == 10
