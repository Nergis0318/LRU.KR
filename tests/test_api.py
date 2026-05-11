import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
async def client():
    """Create async test client"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint returns HTML"""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_shorten_link(client):
    """Test URL shortening"""
    response = await client.post(
        "/api/shorten", json={"url": "https://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_link" in data
    assert "http://test" in data["short_link"]


@pytest.mark.asyncio
async def test_shorten_number_link(client):
    """Test numeric URL shortening"""
    response = await client.post(
        "/api/shorten/number", json={"url": "https://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_link" in data


@pytest.mark.asyncio
async def test_shorten_emoji_link(client):
    """Test emoji URL shortening"""
    response = await client.post(
        "/api/shorten/emoji", json={"url": "https://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_link" in data


@pytest.mark.asyncio
async def test_redirect(client):
    """Test redirect functionality"""
    # First create a short link
    response = await client.post(
        "/api/shorten", json={"url": "https://example.com"}
    )
    data = response.json()
    short_key = data["short_link"].split("/")[-1]

    # Test redirect
    response = await client.get(f"/{short_key}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_cache(client):
    """Test that redirect uses cache on second request"""
    # Create a short link
    response = await client.post(
        "/api/shorten", json={"url": "https://example.com"}
    )
    data = response.json()
    short_key = data["short_link"].split("/")[-1]

    # First redirect (cache miss)
    response1 = await client.get(f"/{short_key}", follow_redirects=False)
    assert response1.status_code == 307

    # Second redirect (should hit cache)
    response2 = await client.get(f"/{short_key}", follow_redirects=False)
    assert response2.status_code == 307
    assert response2.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_nonexistent_key(client):
    """Test 404 for nonexistent key"""
    response = await client.get("/nonexistent123456")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert b"lru_kr_requests_total" in response.content
