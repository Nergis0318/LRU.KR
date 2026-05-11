import asyncio
import time
from statistics import mean, median, stdev

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
async def test_redirect_latency(client):
    """Measure redirect latency"""
    # Create a short link first
    response = await client.post(
        "/api/shorten", json={"url": "https://example.com"}
    )
    short_key = response.json()["short_link"].split("/")[-1]

    # Warm up cache
    await client.get(f"/{short_key}", follow_redirects=False)

    # Measure latency for cached redirects
    latencies = []
    for _ in range(100):
        start = time.time()
        await client.get(f"/{short_key}", follow_redirects=False)
        latencies.append((time.time() - start) * 1000)  # Convert to ms

    print(f"\nRedirect Latency (cached):")
    print(f"  Mean: {mean(latencies):.2f}ms")
    print(f"  Median: {median(latencies):.2f}ms")
    print(f"  Std Dev: {stdev(latencies):.2f}ms")
    print(f"  Min: {min(latencies):.2f}ms")
    print(f"  Max: {max(latencies):.2f}ms")
    print(f"  P95: {sorted(latencies)[94]:.2f}ms")
    print(f"  P99: {sorted(latencies)[98]:.2f}ms")


@pytest.mark.asyncio
async def test_shorten_throughput(client):
    """Measure URL shortening throughput"""
    num_requests = 50
    start = time.time()

    tasks = [
        client.post("/api/shorten", json={"url": f"https://example.com/{i}"})
        for i in range(num_requests)
    ]
    await asyncio.gather(*tasks)

    duration = time.time() - start
    throughput = num_requests / duration

    print(f"\nURL Shortening Throughput:")
    print(f"  Requests: {num_requests}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Throughput: {throughput:.2f} req/s")


@pytest.mark.asyncio
async def test_key_generation_performance(client):
    """Measure key generation performance"""
    num_requests = 100
    latencies = []

    for i in range(num_requests):
        start = time.time()
        await client.post("/api/shorten", json={"url": f"https://example.com/{i}"})
        latencies.append((time.time() - start) * 1000)

    print(f"\nKey Generation Performance:")
    print(f"  Mean: {mean(latencies):.2f}ms")
    print(f"  Median: {median(latencies):.2f}ms")
    print(f"  P95: {sorted(latencies)[94]:.2f}ms")
    print(f"  P99: {sorted(latencies)[98]:.2f}ms")


@pytest.mark.asyncio
async def test_cache_hit_rate(client):
    """Measure cache hit rate"""
    # Create multiple short links
    keys = []
    for i in range(10):
        response = await client.post(
            "/api/shorten", json={"url": f"https://example.com/{i}"}
        )
        keys.append(response.json()["short_link"].split("/")[-1])

    # Access each key multiple times
    for _ in range(10):
        for key in keys:
            await client.get(f"/{key}", follow_redirects=False)

    # Get metrics
    response = await client.get("/metrics")
    metrics = response.text

    # Parse cache metrics
    cache_hits = 0
    cache_misses = 0
    for line in metrics.split("\n"):
        if 'lru_kr_cache_hits_total{cache_type="url"}' in line:
            cache_hits = float(line.split()[-1])
        elif 'lru_kr_cache_misses_total{cache_type="url"}' in line:
            cache_misses = float(line.split()[-1])

    total = cache_hits + cache_misses
    hit_rate = (cache_hits / total * 100) if total > 0 else 0

    print(f"\nCache Performance:")
    print(f"  Cache Hits: {int(cache_hits)}")
    print(f"  Cache Misses: {int(cache_misses)}")
    print(f"  Hit Rate: {hit_rate:.2f}%")

    assert hit_rate > 50, "Cache hit rate should be above 50%"
