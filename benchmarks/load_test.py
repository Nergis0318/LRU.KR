"""
Load testing script for LRU.KR using Locust

Usage:
    locust -f benchmarks/load_test.py --host=http://localhost:2001
"""

from locust import HttpUser, task, between
import random


class LRUKRUser(HttpUser):
    """Simulates a user interacting with LRU.KR"""

    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user session"""
        self.short_keys = []

    @task(3)
    def shorten_url(self):
        """Create a shortened URL (30% of traffic)"""
        url = f"https://example.com/page/{random.randint(1, 10000)}"
        response = self.client.post("/api/shorten", json={"url": url})
        if response.status_code == 200:
            short_link = response.json()["short_link"]
            short_key = short_link.split("/")[-1]
            self.short_keys.append(short_key)

    @task(7)
    def redirect(self):
        """Follow a redirect (70% of traffic)"""
        if self.short_keys:
            short_key = random.choice(self.short_keys)
            self.client.get(f"/{short_key}", allow_redirects=False)
        else:
            # If no keys yet, create one
            self.shorten_url()

    @task(1)
    def shorten_number(self):
        """Create a numeric shortened URL (10% of traffic)"""
        url = f"https://example.com/numeric/{random.randint(1, 10000)}"
        response = self.client.post("/api/shorten/number", json={"url": url})
        if response.status_code == 200:
            short_link = response.json()["short_link"]
            short_key = short_link.split("/")[-1]
            self.short_keys.append(short_key)

    @task(1)
    def shorten_emoji(self):
        """Create an emoji shortened URL (10% of traffic)"""
        url = f"https://example.com/emoji/{random.randint(1, 10000)}"
        response = self.client.post("/api/shorten/emoji", json={"url": url})
        if response.status_code == 200:
            short_link = response.json()["short_link"]
            short_key = short_link.split("/")[-1]
            self.short_keys.append(short_key)

    @task(1)
    def view_metrics(self):
        """Check metrics endpoint (monitoring simulation)"""
        self.client.get("/metrics")


class RedirectHeavyUser(HttpUser):
    """Simulates read-heavy traffic pattern (95% redirects)"""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Initialize with some short keys"""
        self.short_keys = []
        for i in range(10):
            response = self.client.post(
                "/api/shorten", json={"url": f"https://example.com/{i}"}
            )
            if response.status_code == 200:
                short_link = response.json()["short_link"]
                short_key = short_link.split("/")[-1]
                self.short_keys.append(short_key)

    @task(95)
    def redirect(self):
        """Follow redirects (95% of traffic)"""
        if self.short_keys:
            short_key = random.choice(self.short_keys)
            self.client.get(f"/{short_key}", allow_redirects=False)

    @task(5)
    def shorten_url(self):
        """Create new URLs (5% of traffic)"""
        url = f"https://example.com/page/{random.randint(1, 100000)}"
        response = self.client.post("/api/shorten", json={"url": url})
        if response.status_code == 200:
            short_link = response.json()["short_link"]
            short_key = short_link.split("/")[-1]
            self.short_keys.append(short_key)
