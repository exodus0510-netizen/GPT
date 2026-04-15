"""SQLite-backed article deduplication and persistence."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ArticleRecord:
    stock_name: str
    title: str
    link: str
    pub_date: str


class DedupStore:
    """Stores seen articles and prevents duplicate alerts."""

    def __init__(self, db_path: str = "news_store.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    pub_date TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    UNIQUE(stock_name, link)
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_articles_stock_seen
                ON articles(stock_name, first_seen_at DESC);
                """
            )
            conn.commit()

    def insert_if_new(self, record: ArticleRecord) -> bool:
        """Insert an article if not seen before; return True only for new rows."""
        first_seen_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO articles (stock_name, title, link, pub_date, first_seen_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.stock_name,
                    record.title,
                    record.link,
                    record.pub_date,
                    first_seen_at,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def bulk_insert_if_new(self, records: Iterable[ArticleRecord]) -> list[ArticleRecord]:
        new_records: list[ArticleRecord] = []
        for record in records:
            if self.insert_if_new(record):
                new_records.append(record)
        return new_records
