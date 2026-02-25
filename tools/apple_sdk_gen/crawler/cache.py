from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL = 7 * 24 * 3600  # 7 days


class CacheDB:
    def __init__(self, cache_dir: Path, ttl: int = DEFAULT_TTL):
        self._ttl = ttl
        cache_dir.mkdir(parents=True, exist_ok=True)
        db_path = cache_dir / "cache.db"
        self._conn = sqlite3.connect(str(db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                etag TEXT,
                timestamp REAL NOT NULL
            )"""
        )
        self._conn.commit()

    def get(self, url: str) -> dict | None:
        row = self._conn.execute(
            "SELECT data, timestamp FROM cache WHERE url = ?", (url,)
        ).fetchone()
        if row is None:
            return None

        data_str, timestamp = row
        if time.time() - timestamp > self._ttl:
            self._conn.execute("DELETE FROM cache WHERE url = ?", (url,))
            self._conn.commit()
            return None

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return None

    def put(self, url: str, data: dict, etag: str | None = None) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO cache (url, data, etag, timestamp)
               VALUES (?, ?, ?, ?)""",
            (url, json.dumps(data), etag, time.time()),
        )
        self._conn.commit()

    def get_etag(self, url: str) -> str | None:
        row = self._conn.execute(
            "SELECT etag FROM cache WHERE url = ?", (url,)
        ).fetchone()
        return row[0] if row else None

    def size(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM cache").fetchone()
        return row[0] if row else 0

    def clear(self) -> None:
        self._conn.execute("DELETE FROM cache")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
