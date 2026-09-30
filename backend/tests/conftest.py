"""
ChurnSense AI — Backend Test Configuration

pytest configuration with shared fixtures for database, API client,
and test data.
"""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.orm import Organization, User

# Use SQLite for testing (in-memory, no PostgreSQL required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_churnsense.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create fresh tables for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionFactory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with overridden DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a test user."""
    org = Organization(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    user = User(
        email="test@churnsense.ai",
        hashed_password=hash_password("TestPass1"),
        full_name="Test User",
        role="admin",
        organization_id=str(org.id),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Return Authorization headers for the test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
