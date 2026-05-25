"""Local DuckDB vendor: ``get_indicators`` via stockstats on cached OHLCV."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

import pandas as pd
from dateutil.relativedelta import relativedelta
from stockstats import wrap

from ..indicator_library import resolve_tier1_indicator_id, tier1_indicator_descriptions
from ..kite_ohlcv import indicator_bulk_date_range
from ..stockstats_utils import _clean_dataframe
from .store import LocalDataError, MarketDataStore

BEST_IND_PARAMS: Dict[str, str] = tier1_indicator_descriptions()


def _get_stockstats_indicator_bulk(symbol: str, indicator: str, curr_date: str) -> Dict[str, str]:
    start_date_str, end_date_str = indicator_bulk_date_range(curr_date)
    store = MarketDataStore()
    try:
        data = store.load_ohlcv_df(symbol, start_date_str, end_date_str)
    finally:
        store.close()

    if data.empty:
        raise LocalDataError(
            f"No local OHLCV for {symbol} through {curr_date} (need {start_date_str}–{end_date_str}). "
            "Run scripts/prefetch_market_data.py with sufficient --lookback-years."
        )

    data = _clean_dataframe(data)
    df = wrap(data)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    _ = df[indicator]

    result_dict: Dict[str, str] = {}
    for _, row in df.iterrows():
        date_str = str(row["Date"])
        v = row.get(indicator)
        if pd.isna(v):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(v)

    return result_dict


def get_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30,
) -> str:
    """Retrieve technical indicator window from local OHLCV + stockstats."""
    indicator = resolve_tier1_indicator_id(indicator)

    indicator_data = _get_stockstats_indicator_bulk(symbol, indicator, curr_date)
    if not indicator_data:
        return (
            f"## {indicator} values from N/A to {curr_date}:\n\n"
            "N/A: Not a trading day (weekend or holiday)\n\n"
            f"{BEST_IND_PARAMS.get(indicator, 'No description available.')}"
        )

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    current_dt = curr_date_dt
    ind_string = ""
    while current_dt >= before:
        date_str = current_dt.strftime("%Y-%m-%d")
        if date_str in indicator_data:
            indicator_value = indicator_data[date_str]
        else:
            indicator_value = "N/A: Not a trading day (weekend or holiday)"

        ind_string += f"{date_str}: {indicator_value}\n"
        current_dt = current_dt - relativedelta(days=1)

    return (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
        + ind_string
        + "\n\n"
        + BEST_IND_PARAMS.get(indicator, "No description available.")
    )
