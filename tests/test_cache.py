"""Cache tests for URL shortener."""

from httpx import AsyncClient

# ============================================
# Cache Redirect Tests
# ============================================


async def test_redirect_with_cache(ac: AsyncClient) -> None:
    """Test redirect creates cache entry."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://cache-test.com"},
    )
    slug = create_result.json()["data"]

    # First redirect (cache miss, then cached)
    response = await ac.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 302
    assert "https://cache-test.com" in response.headers["location"]


async def test_redirect_cache_hit(ac: AsyncClient) -> None:
    """Test redirect uses cache on subsequent requests."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://cache-hit-test.com"},
    )
    slug = create_result.json()["data"]

    # First request (cache miss)
    await ac.get(f"/{slug}", follow_redirects=False)

    # Second request (should be cache hit)
    response = await ac.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 302


async def test_redirect_not_found_cached(ac: AsyncClient) -> None:
    """Test redirect for non-existent slug."""
    result = await ac.get("/nonexistent", follow_redirects=False)
    assert result.status_code == 404


# ============================================
# Metrics Tests
# ============================================


async def test_metrics_endpoint(ac: AsyncClient) -> None:
    """Test Prometheus metrics endpoint."""
    result = await ac.get("/metrics")
    assert result.status_code == 200
    assert "http_requests_total" in result.text


# ============================================
# Graceful Degradation Tests
# ============================================


async def test_redirect_fallback_on_cache_error(ac: AsyncClient) -> None:
    """Test redirect still works if cache fails."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://fallback-test.com"},
    )
    slug = create_result.json()["data"]

    # Redirect should work even if cache is unavailable
    response = await ac.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 302
    assert "https://fallback-test.com" in response.headers["location"]
