"""Polling scheduler for stock-news monitoring."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from ai_summarizer import AISummarizer
from dedup_store import ArticleRecord, DedupStore
from naver_news import NaverNewsClient
from telegram_sender import TelegramSender

LOGGER = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    stock_names: list[str]
    poll_interval_seconds: int = 60
    news_page_size: int = 20
    ai_enabled: bool = False


class NewsMonitorScheduler:
    def __init__(
        self,
        config: MonitorConfig,
        naver_client: NaverNewsClient,
        store: DedupStore,
        telegram_sender: TelegramSender,
        ai_summarizer: AISummarizer | None = None,
    ) -> None:
        self.config = config
        self.naver_client = naver_client
        self.store = store
        self.telegram_sender = telegram_sender
        self.ai_summarizer = ai_summarizer

    def run_forever(self) -> None:
        LOGGER.info("Starting monitor with stocks=%s", self.config.stock_names)
        while True:
            started = time.time()
            try:
                self.run_once()
            except Exception:
                LOGGER.exception("Unexpected failure in monitoring iteration")

            elapsed = time.time() - started
            sleep_for = max(1, self.config.poll_interval_seconds - int(elapsed))
            LOGGER.debug("Sleeping for %s seconds", sleep_for)
            time.sleep(sleep_for)

    def run_once(self) -> None:
        for stock_name in self.config.stock_names:
            items = self.naver_client.search_news(stock_name, display=self.config.news_page_size)
            records = [
                ArticleRecord(
                    stock_name=stock_name,
                    title=item.title,
                    link=item.link,
                    pub_date=item.pub_date,
                )
                for item in items
                if item.link
            ]
            new_records = self.store.bulk_insert_if_new(records)
            LOGGER.info("Stock='%s': fetched=%s new=%s", stock_name, len(records), len(new_records))

            for record in new_records:
                message = (
                    f"[Naver News Alert]\n"
                    f"Stock: {record.stock_name}\n"
                    f"Title: {record.title}\n"
                    f"Published: {record.pub_date}\n"
                    f"Link: {record.link}"
                )

                if self.config.ai_enabled and self.ai_summarizer:
                    summary = self.ai_summarizer.summarize(
                        stock_name=record.stock_name,
                        title=record.title,
                        link=record.link,
                        pub_date=record.pub_date,
                    )
                    if summary:
                        message = f"{message}\n\n[AI Conservative Analysis]\n{summary}"

                sent = self.telegram_sender.send_message(message)
                if not sent:
                    LOGGER.warning("Failed to send Telegram alert for link=%s", record.link)
