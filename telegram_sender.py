"""Telegram Bot API sender with retry."""

from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOGGER = logging.getLogger(__name__)


class TelegramSender:
    def __init__(self, bot_token: str, chat_id: str, timeout_seconds: int = 10) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout_seconds = timeout_seconds
        self.url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["POST"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def send_message(self, text: str) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        try:
            response = self.session.post(self.url, json=payload, timeout=self.timeout_seconds)
        except requests.RequestException:
            LOGGER.exception("Telegram request failed")
            return False

        if response.status_code != 200:
            LOGGER.error("Telegram API error: %s %s", response.status_code, response.text[:500])
            return False

        return True
