"""Test configuration and async fixtures."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def sync_client():
    """Synchronous test client (deprecated, use async_client instead)."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """
    Async test client using httpx.AsyncClient.

    This fixture demonstrates the best practice of using async client
    from day 0 to avoid event loop issues in integration tests.

    Usage:
        async def test_get_health(async_client):
            response = await async_client.get("/health")
            assert response.status_code == 200
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
