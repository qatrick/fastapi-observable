"""Health check endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_get_health_success(async_client):
    """Test successful health check."""
    response = await async_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "pod_name" in data
    assert "app_version" in data
    assert "timestamp" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_get_health_response_format(async_client):
    """Test health check response format compliance."""
    response = await async_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Verify response model structure
    assert isinstance(data["status"], str)
    assert isinstance(data["pod_name"], str)
    assert isinstance(data["app_version"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["checks"], dict)
