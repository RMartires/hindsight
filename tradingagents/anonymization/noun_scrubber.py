from __future__ import annotations

import re
from typing import Optional

from tradingagents.dataflows.config import get_config
from tradingagents.anonymization.ticker_map import scrub_ticker_text


_CAP_SEQ = re.compile(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b")


def scrub_news_text(text: str, cfg: Optional[dict] = None) -> str:
    """Lightweight proper-noun scrubbing for headlines/news snippets.

    This is intentionally heuristic: it aims to remove obvious company/person/product names
    without adding heavyweight dependencies. It is applied only to news outputs.
    """
    if not text:
        return text
    c = cfg or get_config()
    if not c.get("enable_anonymization"):
        return text

    out = scrub_ticker_text(text, c)
    # Replace multi-word capitalized sequences (e.g., "Foo Bar", "Jane Doe") with a placeholder.
    out = _CAP_SEQ.sub("PROPER_NOUN", out)
    return out

