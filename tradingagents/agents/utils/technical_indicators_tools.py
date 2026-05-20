from langchain_core.tools import tool
from typing import Annotated, Optional

from tradingagents.anonymization.ticker_map import coerce_agent_symbol, deanonymize_ticker, scrub_ticker_text
from tradingagents.agents.utils.core_stock_tools import _normalize_iso_date_arg
from tradingagents.dataflows.config import get_config
from tradingagents.dataflows.indicator_library import resolve_tier1_indicator_id
from tradingagents.dataflows.interface import route_to_vendor


def _resolve_curr_date(param_name: str, raw: Optional[str], cfg: dict) -> str:
    """Prefer explicit arg; otherwise backtest/session ``active_trade_date`` on config."""
    cand = (raw or "").strip()
    if not cand:
        fb = cfg.get("active_trade_date")
        if fb and str(fb).strip():
            return _normalize_iso_date_arg(param_name, str(fb).strip())
        raise ValueError(
            f"{param_name} is required as YYYY-MM-DD when active_trade_date is not set (e.g. live runs)."
        )
    return _normalize_iso_date_arg(param_name, cand)


@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        Optional[str],
        "Current trading date YYYY-MM-DD; omit in backtests to use the session active_trade_date.",
    ] = None,
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """
    Retrieve a single technical indicator for a given ticker symbol.
    Uses the configured technical_indicators vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        indicator (str): A single technical indicator name, e.g. 'rsi', 'macd'. Call this tool once per indicator.
        curr_date (str | None): The current trading date YYYY-MM-DD, or omit during backtests when active_trade_date is set
        look_back_days (int): How many days to look back, default is 30
    Returns:
        str: A formatted dataframe containing the technical indicators for the specified ticker symbol and indicator.
    """
    # LLMs sometimes pass multiple indicators as a comma-separated string;
    # split and process each individually.
    cfg = get_config()
    as_of = _resolve_curr_date("curr_date", curr_date, cfg)
    real = deanonymize_ticker(coerce_agent_symbol(symbol, cfg), cfg)
    indicators = [resolve_tier1_indicator_id(p) for p in (i.strip() for i in indicator.split(",")) if p]
    if len(indicators) > 1:
        results = []
        for ind in indicators:
            results.append(route_to_vendor("get_indicators", real, ind, as_of, look_back_days))
        return scrub_ticker_text("\n\n".join(results), cfg)
    if not indicators:
        raise ValueError("indicator must be a non-empty tier-1 id or comma-separated list of ids.")
    out = route_to_vendor("get_indicators", real, indicators[0], as_of, look_back_days)
    return scrub_ticker_text(out, cfg)