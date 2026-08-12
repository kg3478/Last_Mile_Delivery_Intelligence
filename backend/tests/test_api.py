import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_overview_analytics():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_routes" in data
    assert "on_time_delivery_rate" in data

@pytest.mark.asyncio
async def test_list_routes():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/routes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
