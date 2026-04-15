"""Entry point for Naver stock-news monitor."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from ai_summarizer import AISummarizer
from dedup_store import DedupStore
from naver_news import NaverNewsClient
from scheduler import MonitorConfig, NewsMonitorScheduler
from telegram_sender import TelegramSender


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_config(path: str = "config.yaml") -> MonitorConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Could not find config file: {config_path.resolve()}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    stocks = raw.get("stocks", [])
    if not isinstance(stocks, list) or not stocks:
        raise ValueError("'stocks' must be a non-empty list in config.yaml")

    ai_cfg = raw.get("ai_summarization", {}) or {}

    return MonitorConfig(
        stock_names=[str(s).strip() for s in stocks if str(s).strip()],
        poll_interval_seconds=int(raw.get("poll_interval_seconds", 60)),
        news_page_size=int(raw.get("news_page_size", 20)),
        ai_enabled=bool(ai_cfg.get("enabled", False)),
    )


def build_scheduler() -> NewsMonitorScheduler:
    load_dotenv()  # Helpful for Windows/local runs with a .env file.

    config = load_config()

    naver_client = NaverNewsClient(
        client_id=_required_env("NAVER_CLIENT_ID"),
        client_secret=_required_env("NAVER_CLIENT_SECRET"),
    )
    telegram_sender = TelegramSender(
        bot_token=_required_env("TELEGRAM_BOT_TOKEN"),
        chat_id=_required_env("TELEGRAM_CHAT_ID"),
    )
    store = DedupStore("news_store.db")

    ai_summarizer = None
    if config.ai_enabled:
        ai_summarizer = AISummarizer(
            api_key=_required_env("OPENAI_API_KEY"),
            model=(yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {})
            .get("ai_summarization", {})
            .get("model", "gpt-4.1-mini"),
        )

    return NewsMonitorScheduler(
        config=config,
        naver_client=naver_client,
        store=store,
        telegram_sender=telegram_sender,
        ai_summarizer=ai_summarizer,
    )


def main() -> None:
    setup_logging()
    scheduler = build_scheduler()
    scheduler.run_forever()


if __name__ == "__main__":
    main()
