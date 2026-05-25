from __future__ import annotations

import os
from datetime import datetime
from typing import Dict

from dateutil.relativedelta import relativedelta
from stockstats import wrap

from .config import get_config
from .indicator_library import resolve_tier1_indicator_id, tier1_indicator_descriptions
from .kite_ohlcv import fetch_kite_ohlcv_df, indicator_bulk_date_range
from .kite_common import KiteRateLimitError, maybe_convert_to_kite_rate_limit
from .stockstats_utils import _clean_dataframe


BEST_IND_PARAMS: Dict[str, str] = tier1_indicator_descriptions()


def _get_kite_ohlcv(symbol: str, start_date: str, end_date: str):
    """Fetch OHLCV from Kite (delegates to ``kite_ohlcv.fetch_kite_ohlcv_df``)."""
    return fetch_kite_ohlcv_df(symbol, start_date, end_date)


def _get_stockstats_indicator_bulk(symbol: str, indicator: str, curr_date: str) -> Dict[str, str]:
    """
    Compute the indicator for all trading days in a cached OHLCV range.

    Returns a dict mapping YYYY-MM-DD -> indicator_value (as string).
    """
    import pandas as pd

    cfg = get_config()
    cache_dir = cfg.get("data_cache_dir", "dataflows/data_cache")

    start_date_str, end_date_str = indicator_bulk_date_range(curr_date)

    os.makedirs(cache_dir, exist_ok=True)
    data_file = os.path.join(cache_dir, f"{symbol}-Kite-data-{start_date_str}-{end_date_str}.csv")

    if os.path.exists(data_file):
        data = pd.read_csv(data_file, on_bad_lines="skip")
    else:
        data = _get_kite_ohlcv(symbol, start_date_str, end_date_str)
        if data.empty:
            return {}
        data.to_csv(data_file, index=False)

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
    """
    Retrieve a single technical indicator window around `curr_date`.
    Uses Kite OHLCV + stockstats to compute indicators.
    """
    indicator = resolve_tier1_indicator_id(indicator)

    try:
        indicator_data = _get_stockstats_indicator_bulk(symbol, indicator, curr_date)
        if not indicator_data:
            return f"## {indicator} values from N/A to {curr_date}:\n\nN/A: Not a trading day (weekend or holiday)\n\n{BEST_IND_PARAMS.get(indicator, 'No description available.')}"

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

        result_str = (
            f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
            + ind_string
            + "\n\n"
            + BEST_IND_PARAMS.get(indicator, "No description available.")
        )
        return result_str
    except Exception as e:
        converted = maybe_convert_to_kite_rate_limit(e)
        from .kite_common import KiteRateLimitError as _KiteRateLimitError

        if isinstance(converted, _KiteRateLimitError):
            raise converted
        raise
