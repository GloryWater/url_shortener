"""Authentication API tests."""

from httpx import AsyncClient

# ============================================
# Registration Tests
# ============================================


async def test_register_user(ac: AsyncClient) -> None:
    """Test user registration."""
    result = await ac.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"},
    )
    assert result.status_code == 201
    data = result.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False


async def test_register_user_invalid_email(ac: AsyncClient) -> None:
    """Test registration with invalid email."""
    result = await ac.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "SecurePass123!"},
    )
    assert result.status_code == 422


async def test_register_user_short_password(ac: AsyncClient) -> None:
    """Test registration with short password."""
    result = await ac.post(
        "/api/v1/auth/register",
        json={"email": "test2@example.com", "password": "short"},
    )
    assert result.status_code == 422


async def test_register_duplicate_email(ac: AsyncClient) -> None:
    """Test registration with duplicate email."""
    # Register first user
    await ac.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "SecurePass123!"},
    )

    # Try to register with same email
    result = await ac.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "SecurePass123!"},
    )
    assert result.status_code == 400


# ============================================
# Login Tests
# ============================================


async def test_login_user(ac: AsyncClient) -> None:
    """Test user login."""
    # Register user first
    await ac.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "SecurePass123!"},
    )

    # Login
    result = await ac.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "SecurePass123!"},
    )
    assert result.status_code == 200
    data = result.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_credentials(ac: AsyncClient) -> None:
    """Test login with invalid credentials."""
    result = await ac.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPass123!"},
    )
    assert result.status_code == 401


async def test_login_wrong_password(ac: AsyncClient) -> None:
    """Test login with wrong password."""
    # Register user
    await ac.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "SecurePass123!"},
    )

    # Try wrong password
    result = await ac.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPass123!"},
    )
    assert result.status_code == 401


# ============================================
# Get Current User Tests
# ============================================


async def test_get_current_user(ac: AsyncClient) -> None:
    """Test getting current authenticated user."""
    # Register and login
    await ac.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "SecurePass123!"},
    )

    login_result = await ac.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "SecurePass123!"},
    )
    token = login_result.json()["access_token"]

    # Get current user
    result = await ac.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert result.status_code == 200
    data = result.json()
    assert data["email"] == "me@example.com"


async def test_get_current_user_unauthenticated(ac: AsyncClient) -> None:
    """Test getting current user without authentication."""
    result = await ac.get("/api/v1/auth/me")
    assert result.status_code == 401


async def test_get_current_user_invalid_token(ac: AsyncClient) -> None:
    """Test getting current user with invalid token."""
    result = await ac.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert result.status_code == 401


async def test_get_current_user_expired_token(ac: AsyncClient) -> None:
    """Test getting current user with expired token."""
    # Create an expired token (manually crafted for testing)
    expired_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjowfQ.invalid"
    )
    result = await ac.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert result.status_code == 401
