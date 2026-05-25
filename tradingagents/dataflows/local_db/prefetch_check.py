"""Verify DuckDB has OHLCV for backtest dates before offline runs."""

from __future__ import annotations

from typing import List, Sequence

from .store import LocalDataError, MarketDataStore, normalize_symbol_key, trading_weekdays_in_range


def verify_local_ohlcv_coverage(
    symbol: str,
    dates: Sequence[str],
    *,
    db_path: str | None = None,
) -> None:
    """
    Raise ``LocalDataError`` if any weekday in ``dates`` lacks a cached OHLCV row.
    """
    trade_dates = trading_weekdays_in_range(dates)
    if not trade_dates:
        return

    sym = normalize_symbol_key(symbol)
    store = MarketDataStore(db_path=db_path) if db_path else MarketDataStore()
    try:
        present = store.dates_present(sym, trade_dates)
    finally:
        store.close()

    missing = [d for d in trade_dates if d not in present]
    if missing:
        preview = ", ".join(missing[:5])
        suffix = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
        raise LocalDataError(
            f"Local cache missing {len(missing)} weekday(s) for {sym}: {preview}{suffix}. "
            f"Run: python scripts/prefetch_market_data.py --ticker {sym} --dates-csv <schedule.csv>"
        )
