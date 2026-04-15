"""Client for Naver News Search API with retries."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from html import unescape
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOGGER = logging.getLogger(__name__)

NAVER_API_URL = "https://openapi.naver.com/v1/search/news.json"


@dataclass(frozen=True)
class NaverNewsItem:
    title: str
    link: str
    pub_date: str


class NaverNewsClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

        retry = Retry(
            total=max_retries,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    @staticmethod
    def _clean_html(text: str) -> str:
        # Naver titles include <b> tags around highlighted terms.
        return unescape(text.replace("<b>", "").replace("</b>", ""))

    def search_news(self, query: str, display: int = 20) -> list[NaverNewsItem]:
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        params = {
            "query": query,
            "display": max(1, min(display, 100)),
            "sort": "date",
        }
        response = self.session.get(
            NAVER_API_URL,
            headers=headers,
            params=params,
            timeout=self.timeout_seconds,
        )
        if response.status_code != 200:
            LOGGER.error(
                "Naver API error for query='%s': %s %s",
                query,
                response.status_code,
                response.text[:500],
            )
            return []

        payload: dict[str, Any] = response.json()
        items = payload.get("items", [])
        parsed: list[NaverNewsItem] = []
        for item in items:
            parsed.append(
                NaverNewsItem(
                    title=self._clean_html(item.get("title", "").strip()),
                    link=item.get("link", "").strip(),
                    pub_date=item.get("pubDate", "").strip(),
                )
            )
        return parsed
