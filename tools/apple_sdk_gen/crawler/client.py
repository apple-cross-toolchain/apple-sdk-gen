from __future__ import annotations

import asyncio
import logging
import time

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://developer.apple.com/tutorials/data"


class RateLimiter:
    def __init__(self, rate: float = 10.0):
        self._rate = rate
        self._tokens = rate
        self._max_tokens = rate
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self._max_tokens, self._tokens + elapsed * self._rate)
            self._last_refill = now

            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


class APIClient:
    def __init__(
        self,
        concurrency: int = 10,
        rate_limit: float = 10.0,
        max_retries: int = 3,
        cache: "CacheDB | None" = None,
    ):
        self._semaphore = asyncio.Semaphore(concurrency)
        self._rate_limiter = RateLimiter(rate_limit)
        self._max_retries = max_retries
        self._cache = cache
        self._client: httpx.AsyncClient | None = None
        self._stats = {"requests": 0, "cache_hits": 0, "errors": 0}

    async def __aenter__(self) -> APIClient:
        self._client = httpx.AsyncClient(
            http2=True,
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={
                "Accept": "application/json",
                "User-Agent": "apple-sdk-gen/0.1",
            },
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    async def fetch_json(self, url: str) -> dict | None:
        # Check cache first
        if self._cache:
            cached = self._cache.get(url)
            if cached is not None:
                self._stats["cache_hits"] += 1
                return cached

        async with self._semaphore:
            for attempt in range(self._max_retries):
                await self._rate_limiter.acquire()
                try:
                    assert self._client is not None
                    self._stats["requests"] += 1
                    resp = await self._client.get(url)

                    if resp.status_code == 404:
                        logger.debug("404 for %s", url)
                        return None

                    if resp.status_code == 429:
                        retry_after = float(resp.headers.get("Retry-After", "5"))
                        logger.warning("Rate limited, waiting %.1fs", retry_after)
                        await asyncio.sleep(retry_after)
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                    if self._cache:
                        etag = resp.headers.get("ETag")
                        self._cache.put(url, data, etag=etag)

                    return data

                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500:
                        wait = 2 ** attempt
                        logger.warning(
                            "Server error %d for %s, retrying in %ds",
                            e.response.status_code, url, wait,
                        )
                        await asyncio.sleep(wait)
                        continue
                    self._stats["errors"] += 1
                    logger.error("HTTP error for %s: %s", url, e)
                    return None

                except (httpx.RequestError, httpx.TimeoutException) as e:
                    wait = 2 ** attempt
                    logger.warning(
                        "Request error for %s: %s, retrying in %ds",
                        url, e, wait,
                    )
                    await asyncio.sleep(wait)
                    continue

            self._stats["errors"] += 1
            logger.error("Failed after %d retries: %s", self._max_retries, url)
            return None

    async def fetch_doc(self, doc_path: str) -> dict | None:
        if doc_path.startswith("doc://"):
            # Extract path from doc:// URI
            # doc://com.apple.foundation/documentation/Foundation/NSString
            # -> /documentation/Foundation/NSString
            parts = doc_path.split("/documentation/", 1)
            if len(parts) == 2:
                doc_path = "/documentation/" + parts[1]
            else:
                logger.warning("Cannot parse doc URI: %s", doc_path)
                return None

        url = f"{BASE_URL}{doc_path}.json"
        return await self.fetch_json(url)
