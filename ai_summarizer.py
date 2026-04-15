"""Optional conservative AI summary module using OpenAI Responses API."""

from __future__ import annotations

import json
import logging

from openai import OpenAI

LOGGER = logging.getLogger(__name__)


class AISummarizer:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def summarize(self, stock_name: str, title: str, link: str, pub_date: str) -> str | None:
        prompt = f"""
You are a conservative financial-news assistant.
Analyze ONE article headline and provide cautious, uncertainty-aware insight.

Article metadata:
- stock_name: {stock_name}
- title: {title}
- link: {link}
- pubDate: {pub_date}

Output in JSON with EXACT keys:
1) stock_name
2) sentiment  (bullish | bearish | neutral)
3) key_catalyst
4) short_term_trading_checkpoint
5) caution_note

Rules:
- If the title is ambiguous, sentiment must be neutral.
- Explicitly mention uncertainty and limits of headline-only inference.
- Do not provide definitive investment advice.
""".strip()
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=220,
            )
        except Exception:
            LOGGER.exception("OpenAI Responses API call failed")
            return None

        text_output = getattr(response, "output_text", None)
        if not text_output:
            LOGGER.warning("No text output from OpenAI response")
            return None

        try:
            parsed = json.loads(text_output)
        except json.JSONDecodeError:
            LOGGER.warning("OpenAI output was not JSON. Returning raw text snippet.")
            return f"AI analysis (unstructured):\n{text_output[:700]}"

        lines = [
            f"1) stock name: {parsed.get('stock_name', stock_name)}",
            f"2) sentiment: {parsed.get('sentiment', 'neutral')}",
            f"3) key catalyst: {parsed.get('key_catalyst', 'Uncertain from headline only.')}",
            (
                "4) short-term trading checkpoint: "
                f"{parsed.get('short_term_trading_checkpoint', 'Wait for confirmed details and price/volume reaction.')}"
            ),
            f"5) caution note: {parsed.get('caution_note', 'Headline-only analysis is uncertain and may be misleading.')}"
        ]
        return "\n".join(lines)
