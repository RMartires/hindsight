"""Simulation / backtest date context for data vendors.

When ``simulation_data_end`` is set in config (typically from ``TradingAgentsGraph.propagate``),
all OHLCV and tool date ranges must not extend past this calendar date so historical backtests
do not download data through wall-clock *today*.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from tradingagents.dataflows.config import get_config


def simulation_data_end_policy() -> str:
    """Return ``prior_calendar_day`` or ``trade_date`` (inclusive)."""
    cfg = get_config()
    p = (cfg.get("simulation_data_end_policy") or "prior_calendar_day").strip().lower()
    if p in ("trade_date", "prior_calendar_day"):
        return p
    return "prior_calendar_day"


def effective_simulation_end_date_str(trade_date: str) -> str:
    """Upper bound for *information date* (YYYY-MM-DD) used for downloads and clamps.

    - ``prior_calendar_day`` (default): calendar day before ``trade_date`` (conservative).
    - ``trade_date``: use ``trade_date`` as the max inclusive date.
    """
    d = datetime.strptime(trade_date.strip(), "%Y-%m-%d")
    if simulation_data_end_policy() == "trade_date":
        return d.strftime("%Y-%m-%d")
    return (d - timedelta(days=1)).strftime("%Y-%m-%d")


def get_simulation_data_end_configured() -> Optional[str]:
    """Explicit cap from config (set during ``propagate``), or None for live mode."""
    cfg = get_config()
    raw = cfg.get("simulation_data_end")
    if raw is None or str(raw).strip() == "":
        return None
    return str(raw).strip()[:10]


def effective_data_end_date() -> str:
    """Max inclusive calendar date for price/indicator downloads.

    If ``simulation_data_end`` is set in config, returns it.
    Otherwise returns today's calendar date (local), matching prior yfinance/stockstats behavior.
    """
    configured = get_simulation_data_end_configured()
    if configured:
        return configured
    return pd.Timestamp.today().strftime("%Y-%m-%d")


def clamp_date_str(d: str) -> str:
    """Clamp ISO date string to ``<= effective_data_end_date()``."""
    cap = effective_data_end_date()
    ds = str(d).strip()[:10]
    if not ds:
        return cap
    return min(ds, cap)


def clamp_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Clamp both ends to the simulation cap; ensure ``start <= end``."""
    cap = effective_data_end_date()
    s = min(str(start_date).strip()[:10], cap)
    e = min(str(end_date).strip()[:10], cap)
    if s > e:
        s = e
    return s, e
