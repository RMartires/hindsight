"""Shared Kite historical OHLCV fetch and DataFrame normalization."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from .kite_common import KiteRateLimitError, get_kite_session, maybe_convert_to_kite_rate_limit
from .kite_instruments import get_instrument_mapper

_log = logging.getLogger(__name__)

_HISTORICAL_MAX_ATTEMPTS = 4
_HISTORICAL_RETRY_BASE_DELAY_SEC = 2.0

OHLCV_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]


def records_to_ohlcv_df(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Normalize Kite ``historical_data`` records to a standard OHLCV DataFrame."""
    if not records:
        return pd.DataFrame(columns=OHLCV_COLUMNS)

    df = pd.DataFrame.from_records(records)
    if "date" in df.columns:
        df = df.rename(columns={"date": "Date"})

    rename_map = {}
    for k in ["open", "high", "low", "close", "volume"]:
        if k in df.columns:
            rename_map[k] = k.capitalize() if k != "volume" else "Volume"
    if rename_map:
        df = df.rename(columns=rename_map)

    if "Close" in df.columns and "Adj Close" not in df.columns:
        df["Adj Close"] = df["Close"]

    keep = [c for c in OHLCV_COLUMNS if c in df.columns]
    df = df[keep]

    numeric_columns = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Volume" in df.columns:
        df["Volume"] = df["Volume"].fillna(0).astype("int64", errors="ignore")
    for col in ["Open", "High", "Low", "Close", "Adj Close"]:
        if col in df.columns:
            df[col] = df[col].round(2)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df


def fetch_kite_ohlcv_df(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV from Kite for ``symbol`` between inclusive calendar dates.

    Returns DataFrame with Date (datetime), Open, High, Low, Close, Adj Close, Volume.
    """
    mapper = get_instrument_mapper()
    resolved = mapper.resolve(symbol)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    records: List[Dict[str, Any]] | None = None
    for attempt in range(_HISTORICAL_MAX_ATTEMPTS):
        try:
            kite = get_kite_session().get_client()
            records = kite.historical_data(
                resolved["instrument_token"],
                start_dt,
                end_dt,
                interval="day",
            )
            break
        except Exception as e:
            converted = maybe_convert_to_kite_rate_limit(e)
            if isinstance(converted, KiteRateLimitError):
                raise converted from e
            transient = isinstance(
                e,
                (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    ConnectionResetError,
                ),
            )
            if transient and attempt + 1 < _HISTORICAL_MAX_ATTEMPTS:
                delay = _HISTORICAL_RETRY_BASE_DELAY_SEC * (attempt + 1)
                _log.warning(
                    "Kite historical_data %s %s–%s failed (%s/%s): %s; retry in %.1fs",
                    symbol,
                    start_date,
                    end_date,
                    attempt + 1,
                    _HISTORICAL_MAX_ATTEMPTS,
                    e,
                    delay,
                )
                time.sleep(delay)
                continue
            raise

    assert records is not None
    return records_to_ohlcv_df(records)


def indicator_bulk_date_range(curr_date: str) -> tuple[str, str]:
    """Start/end (YYYY-MM-DD) for 15y indicator bulk, capped by Kite max interval."""
    from datetime import timedelta

    from dateutil.relativedelta import relativedelta

    from .kite_common import KITE_HISTORICAL_MAX_INTERVAL_DAYS

    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    ideal_start = end_dt - relativedelta(years=15)
    max_span_start = end_dt - timedelta(days=KITE_HISTORICAL_MAX_INTERVAL_DAYS - 1)
    start_dt = max(ideal_start, max_span_start)
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")
