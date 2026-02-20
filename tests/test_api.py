"""API tests for URL shortener."""

from httpx import AsyncClient

# ============================================
# Basic URL Shortening Tests
# ============================================


async def test_create_short_url(ac: AsyncClient) -> None:
    """Test creating a short URL."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com"},
    )
    assert result.status_code == 200
    data = result.json()
    assert "data" in data
    assert len(data["data"]) == 6
    assert "short_url" in data
    assert "long_url" in data


async def test_create_short_url_invalid_url(ac: AsyncClient) -> None:
    """Test creating short URL with invalid URL."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "not-a-url"},
    )
    assert result.status_code == 422


async def test_create_short_url_missing_field(ac: AsyncClient) -> None:
    """Test creating short URL with missing long_url field."""
    result = await ac.post("/api/v1/urls", json={})
    assert result.status_code == 422


# ============================================
# Custom Slug Tests
# ============================================


async def test_create_short_url_with_custom_slug(ac: AsyncClient) -> None:
    """Test creating short URL with custom slug."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "custom_slug": "mylink"},
    )
    assert result.status_code == 200
    data = result.json()
    assert data["data"] == "mylink"
    assert data["custom_slug"] is True


async def test_create_short_url_custom_slug_too_short(ac: AsyncClient) -> None:
    """Test custom slug validation (too short)."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "custom_slug": "ab"},
    )
    assert result.status_code == 422


async def test_create_short_url_custom_slug_too_long(ac: AsyncClient) -> None:
    """Test custom slug validation (too long)."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "custom_slug": "thisistoolong123"},
    )
    assert result.status_code == 422


async def test_create_short_url_custom_slug_invalid_chars(ac: AsyncClient) -> None:
    """Test custom slug validation (invalid characters)."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "custom_slug": "my-link"},
    )
    assert result.status_code == 422


async def test_create_short_url_duplicate_custom_slug(ac: AsyncClient) -> None:
    """Test creating short URL with duplicate custom slug."""
    # Create first URL
    await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "custom_slug": "testlink"},
    )

    # Try to create second URL with same slug
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://other.com", "custom_slug": "testlink"},
    )
    assert result.status_code == 409


# ============================================
# Expiration Tests
# ============================================


async def test_create_short_url_with_expiration(ac: AsyncClient) -> None:
    """Test creating short URL with expiration."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "expires_in_days": 30},
    )
    assert result.status_code == 200
    data = result.json()
    assert data["expires_at"] is not None


async def test_create_short_url_expiration_invalid(ac: AsyncClient) -> None:
    """Test expiration validation (negative days)."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "expires_in_days": -5},
    )
    assert result.status_code == 422


async def test_create_short_url_expiration_too_long(ac: AsyncClient) -> None:
    """Test expiration validation (too many days)."""
    result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com", "expires_in_days": 400},
    )
    assert result.status_code == 422


# ============================================
# Redirect Tests
# ============================================


async def test_redirect_to_url(ac: AsyncClient) -> None:
    """Test redirecting to original URL."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com/test"},
    )
    slug = create_result.json()["data"]

    # Test redirect
    response = await ac.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 302
    assert "https://example.com/test" in response.headers["location"]


async def test_redirect_not_found(ac: AsyncClient) -> None:
    """Test redirect for non-existent slug."""
    result = await ac.get("/nonexistent", follow_redirects=False)
    assert result.status_code == 404


# ============================================
# URL Info Tests
# ============================================


async def test_get_url_info(ac: AsyncClient) -> None:
    """Test getting URL information."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com"},
    )
    slug = create_result.json()["data"]

    # Get URL info
    result = await ac.get(f"/api/v1/urls/{slug}")
    assert result.status_code == 200
    data = result.json()
    assert data["slug"] == slug
    assert "click_count" in data
    assert "created_at" in data


async def test_get_url_info_not_found(ac: AsyncClient) -> None:
    """Test getting non-existent URL info."""
    result = await ac.get("/api/v1/urls/nonexistent")
    assert result.status_code == 404


# ============================================
# Delete URL Tests
# ============================================


async def test_delete_url(ac: AsyncClient) -> None:
    """Test deleting a URL."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com"},
    )
    slug = create_result.json()["data"]

    # Delete URL
    delete_result = await ac.delete(f"/api/v1/urls/{slug}")
    assert delete_result.status_code == 200
    assert delete_result.json()["success"] is True

    # Verify URL is deleted
    get_result = await ac.get(f"/api/v1/urls/{slug}")
    assert get_result.status_code == 404


async def test_delete_url_not_found(ac: AsyncClient) -> None:
    """Test deleting non-existent URL."""
    result = await ac.delete("/api/v1/urls/nonexistent")
    assert result.status_code == 404


# ============================================
# List URLs Tests
# ============================================


async def test_list_urls(ac: AsyncClient) -> None:
    """Test listing URLs with pagination."""
    # Create some URLs
    for i in range(5):
        await ac.post("/api/v1/urls", json={"long_url": f"https://example{i}.com"})

    result = await ac.get("/api/v1/urls?page=1&limit=10")
    assert result.status_code == 200
    data = result.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert data["total"] >= 5


async def test_list_urls_pagination(ac: AsyncClient) -> None:
    """Test URL list pagination."""
    # Create 25 URLs
    for i in range(25):
        await ac.post("/api/v1/urls", json={"long_url": f"https://example{i}.com"})

    # Get first page
    result1 = await ac.get("/api/v1/urls?page=1&limit=10")
    data1 = result1.json()
    assert data1["page"] == 1
    assert data1["limit"] == 10
    assert len(data1["items"]) == 10

    # Get second page
    result2 = await ac.get("/api/v1/urls?page=2&limit=10")
    data2 = result2.json()
    assert data2["page"] == 2
    assert len(data2["items"]) == 10


# ============================================
# Analytics Tests
# ============================================


async def test_get_url_stats(ac: AsyncClient) -> None:
    """Test getting URL click statistics."""
    # Create short URL
    create_result = await ac.post(
        "/api/v1/urls",
        json={"long_url": "https://example.com"},
    )
    slug = create_result.json()["data"]

    # Simulate clicks by accessing the URL
    await ac.get(f"/{slug}", follow_redirects=False)
    await ac.get(f"/{slug}", follow_redirects=False)

    # Get stats
    result = await ac.get(f"/api/v1/urls/{slug}/stats")
    assert result.status_code == 200
    data = result.json()
    assert "total_clicks" in data
    assert data["total_clicks"] >= 2


# ============================================
# Duplicate URL Detection Tests
# ============================================


async def test_duplicate_url_detection(ac: AsyncClient) -> None:
    """Test that duplicate URLs return existing slug."""
    long_url = "https://duplicate-test.com"

    # Create first URL
    result1 = await ac.post("/api/v1/urls", json={"long_url": long_url})
    slug1 = result1.json()["data"]

    # Create duplicate URL
    result2 = await ac.post("/api/v1/urls", json={"long_url": long_url})
    slug2 = result2.json()["data"]

    # Should return same slug
    assert slug1 == slug2


# ============================================
# Health Check Tests
# ============================================


async def test_health_check(ac: AsyncClient) -> None:
    """Test health check endpoint."""
    result = await ac.get("/health")
    assert result.status_code == 200
    data = result.json()
    assert "status" in data
    assert "version" in data
    assert "database" in data


# ============================================
# Legacy Endpoint Tests
# ============================================


async def test_legacy_create_endpoint(ac: AsyncClient) -> None:
    """Test legacy /short_url endpoint."""
    result = await ac.post("/short_url", json={"long_url": "https://example.com"})
    assert result.status_code == 200
    data = result.json()
    assert "data" in data


# ============================================
# Edge Cases Tests
# ============================================


async def test_url_with_special_characters(ac: AsyncClient) -> None:
    """Test URL with special characters."""
    long_url = "https://example.com/path?param=value&other=123#anchor"
    result = await ac.post("/api/v1/urls", json={"long_url": long_url})
    assert result.status_code == 200


async def test_url_with_unicode(ac: AsyncClient) -> None:
    """Test URL with unicode characters."""
    long_url = "https://example.com/путь/с/юникодом"
    result = await ac.post("/api/v1/urls", json={"long_url": long_url})
    assert result.status_code == 200


async def test_very_long_url(ac: AsyncClient) -> None:
    """Test very long URL."""
    long_url = "https://example.com/" + "a" * 1000
    result = await ac.post("/api/v1/urls", json={"long_url": long_url})
    assert result.status_code == 200


async def test_url_without_https(ac: AsyncClient) -> None:
    """Test URL without HTTPS."""
    long_url = "http://example.com"
    result = await ac.post("/api/v1/urls", json={"long_url": long_url})
    assert result.status_code == 200


# ============================================
# Slug Uniqueness Tests
# ============================================


async def test_generate_multiple_slugs_unique(ac: AsyncClient) -> None:
    """Test uniqueness of generated slugs."""
    slugs: set[str] = set()
    # Use different URLs to avoid duplicate detection
    for i in range(20):
        result = await ac.post(
            "/api/v1/urls",
            json={"long_url": f"https://unique-test{i}.com"},
        )
        assert result.status_code == 200
        slugs.add(result.json()["data"])

    # All slugs should be unique
    assert len(slugs) == 20
