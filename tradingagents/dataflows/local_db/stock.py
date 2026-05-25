"""Local DuckDB vendor: ``get_stock_data``."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from .store import LocalDataError, MarketDataStore, normalize_symbol_key


def format_ohlcv_block(
    symbol: str,
    start_date: str,
    end_date: str,
    df: pd.DataFrame,
) -> str:
    """Format OHLCV DataFrame as Kite/yfinance-compatible CSV string."""
    if df.empty:
        return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    out = out.dropna(subset=["Date"])
    numeric_columns = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in out.columns]
    for col in numeric_columns:
        if col == "Volume":
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce").round(2)

    csv_string = out.to_csv(index=False)
    header = f"# Stock data for {normalize_symbol_key(symbol)} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(out)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += "# Source: local DuckDB cache\n\n"
    return header + csv_string


def get_stock_data(symbol: str, start_date: str, end_date: str) -> str:
    """Retrieve OHLCV from local DuckDB for the given date range."""
    store = MarketDataStore()
    try:
        df = store.load_ohlcv_df(symbol, start_date, end_date)
    finally:
        store.close()

    if df.empty:
        raise LocalDataError(
            f"No local OHLCV for {normalize_symbol_key(symbol)} between {start_date} and {end_date}. "
            "Run: python scripts/prefetch_market_data.py --ticker "
            f"{normalize_symbol_key(symbol)} --dates-csv <schedule.csv>"
        )

    return format_ohlcv_block(symbol, start_date, end_date, df)
