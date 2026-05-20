from datetime import datetime

from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config
from tradingagents.anonymization.ticker_map import (
    coerce_agent_symbol,
    deanonymize_ticker,
    scrub_ticker_text,
)


def _repair_llm_calendar_typos(raw: str) -> str:
    """Normalize one common LLM date typo: duplicated first year digit adds an 11th character.

    Example: ``22025-01-31`` → ``2025-01-31``. Only accepts the repair when the trimmed
    string is a valid ``%Y-%m-%d``.
    """
    t = (raw or "").strip()
    if (
        len(t) == 11
        and t[0].isdigit()
        and t[0] == t[1]
        and t[5] == "-" == t[8]
    ):
        candidate = t[1:]
        if len(candidate) == 10:
            try:
                datetime.strptime(candidate, "%Y-%m-%d")
            except ValueError:
                return t
            return candidate
    return t


def _normalize_iso_date_arg(param_name: str, raw: str) -> str:
    """Require a full YYYY-MM-DD string; models sometimes emit truncated dates (e.g. '2024-')."""
    s = _repair_llm_calendar_typos(raw)
    if len(s) != 10 or s[4] != "-" or s[7] != "-":
        raise ValueError(
            f"{param_name} must be a complete calendar date in YYYY-MM-DD (e.g. 2024-05-10); "
            f"received {raw!r}. Do not truncate month or day."
        )
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(
            f"{param_name} must be a valid calendar date in YYYY-MM-DD; received {raw!r}."
        ) from e
    return s


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[
        str,
        "Start date: full YYYY-MM-DD only (e.g. 2024-04-10). Never omit day or use partial strings.",
    ],
    end_date: Annotated[
        str,
        "End date: full YYYY-MM-DD only (e.g. 2024-05-10). Never omit day or use partial strings.",
    ],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
    """
    start_date = _normalize_iso_date_arg("start_date", start_date)
    end_date = _normalize_iso_date_arg("end_date", end_date)
    cfg = get_config()
    real = deanonymize_ticker(coerce_agent_symbol(symbol, cfg), cfg)
    out = route_to_vendor("get_stock_data", real, start_date, end_date)
    return scrub_ticker_text(out, cfg)
