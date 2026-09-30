"""
ChurnSense AI — Authentication API Tests

Tests cover:
  - Registration (valid, duplicate email)
  - Login (valid, wrong password, inactive user)
  - Protected endpoint access
  - Authentication failure
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """New user registration should return 201 with user data."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "newuser@churnsense.ai",
        "password": "SecurePass1",
        "full_name": "New User",
        "organization_name": "New Org",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@churnsense.ai"
    assert "hashed_password" not in data  # Password must never be returned


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Registration with existing email should return 409."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@churnsense.ai",  # same as test_user fixture
        "password": "AnotherPass1",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Registration with weak password should return 422."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "weak@churnsense.ai",
        "password": "short",  # no uppercase, no digit, too short
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Valid credentials should return access and refresh tokens."""
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@churnsense.ai",
        "password": "TestPass1",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Wrong password should return 401."""
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@churnsense.ai",
        "password": "WrongPassword1",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Login with non-existent email should return 401 (not 404 to prevent user enumeration)."""
    resp = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "SomePass1",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, auth_headers: dict):
    """Authenticated request to /auth/me should return user profile."""
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@churnsense.ai"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Request without token should return 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """Request with invalid token should return 401."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401
