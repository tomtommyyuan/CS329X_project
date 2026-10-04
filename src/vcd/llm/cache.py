from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional


class SqliteCache:
    """Key -> JSON string. One table, WAL mode, safe for a single process with async tasks."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL, created REAL NOT NULL)")
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            row = self.conn.execute("SELECT value FROM cache WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def put(self, key: str, value: str) -> None:
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO cache (key, value, created) VALUES (?, ?, ?)", (key, value, time.time()))
            self.conn.commit()

    def __len__(self) -> int:
        with self._lock:
            return int(self.conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0])
