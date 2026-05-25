"""DuckDB store for prefetched OHLCV bars."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import duckdb
import pandas as pd

from tradingagents.dataflows.config import get_config

from ..kite_ohlcv import OHLCV_COLUMNS


class LocalDataError(RuntimeError):
    """Raised when local DuckDB cache is missing required market data."""


def normalize_symbol_key(symbol: str) -> str:
    """Canonical symbol key for DB rows (uppercase, stripped)."""
    return symbol.strip().upper()


def resolve_market_db_path(config: Optional[dict] = None) -> str:
    cfg = config or get_config()
    explicit = (cfg.get("market_db_path") or os.getenv("MARKET_DB_PATH", "")).strip()
    if explicit:
        return explicit
    cache_dir = cfg.get("data_cache_dir", "dataflows/data_cache")
    return os.path.join(cache_dir, "market.duckdb")


class MarketDataStore:
    """DuckDB-backed OHLCV cache."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS ohlcv (
        symbol      VARCHAR NOT NULL,
        date        DATE NOT NULL,
        open        DOUBLE,
        high        DOUBLE,
        low         DOUBLE,
        close       DOUBLE,
        volume      BIGINT,
        adj_close   DOUBLE,
        source      VARCHAR NOT NULL DEFAULT 'kite',
        fetched_at  TIMESTAMP NOT NULL,
        PRIMARY KEY (symbol, date)
    );
    """

    def __init__(self, db_path: Optional[str] = None, config: Optional[dict] = None):
        self._db_path = db_path or resolve_market_db_path(config)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(self._db_path)
        self._conn.execute(self._SCHEMA)

    @property
    def db_path(self) -> str:
        return self._db_path

    def close(self) -> None:
        self._conn.close()

    def upsert_ohlcv_df(
        self,
        symbol: str,
        df: pd.DataFrame,
        *,
        source: str = "kite",
        fetched_at: Optional[datetime] = None,
    ) -> int:
        """Insert or replace OHLCV rows for ``symbol``. Returns row count written."""
        if df.empty:
            return 0

        sym = normalize_symbol_key(symbol)
        ts = fetched_at or datetime.now()
        work = df.copy()
        if "Date" not in work.columns:
            raise ValueError("OHLCV DataFrame must include Date column")

        work["date"] = pd.to_datetime(work["Date"], errors="coerce").dt.date
        work = work.dropna(subset=["date"])
        if work.empty:
            return 0

        rows = []
        for _, row in work.iterrows():
            rows.append(
                (
                    sym,
                    row["date"],
                    float(row["Open"]) if pd.notna(row.get("Open")) else None,
                    float(row["High"]) if pd.notna(row.get("High")) else None,
                    float(row["Low"]) if pd.notna(row.get("Low")) else None,
                    float(row["Close"]) if pd.notna(row.get("Close")) else None,
                    int(row["Volume"]) if pd.notna(row.get("Volume")) else None,
                    float(row.get("Adj Close", row.get("Close")))
                    if pd.notna(row.get("Adj Close", row.get("Close")))
                    else None,
                    source,
                    ts,
                )
            )

        self._conn.executemany(
            """
            INSERT OR REPLACE INTO ohlcv
            (symbol, date, open, high, low, close, volume, adj_close, source, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        return len(rows)

    def load_ohlcv_df(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Load OHLCV as a DataFrame with Date column (datetime64)."""
        sym = normalize_symbol_key(symbol)
        result = self._conn.execute(
            """
            SELECT date, open, high, low, close, volume, adj_close
            FROM ohlcv
            WHERE symbol = ? AND date >= ? AND date <= ?
            ORDER BY date
            """,
            [sym, start_date, end_date],
        ).fetchdf()

        if result.empty:
            return pd.DataFrame(columns=OHLCV_COLUMNS)

        out = pd.DataFrame(
            {
                "Date": pd.to_datetime(result["date"]),
                "Open": result["open"],
                "High": result["high"],
                "Low": result["low"],
                "Close": result["close"],
                "Adj Close": result["adj_close"].fillna(result["close"]),
                "Volume": result["volume"],
            }
        )
        return out

    def dates_present(self, symbol: str, dates: Sequence[str]) -> set[str]:
        """Return subset of ``dates`` (YYYY-MM-DD) that exist in the cache."""
        if not dates:
            return set()
        sym = normalize_symbol_key(symbol)
        placeholders = ", ".join(["?"] * len(dates))
        rows = self._conn.execute(
            f"""
            SELECT CAST(date AS VARCHAR) AS d
            FROM ohlcv
            WHERE symbol = ? AND CAST(date AS VARCHAR) IN ({placeholders})
            """,
            [sym, *dates],
        ).fetchall()
        return {r[0][:10] for r in rows}

    def count_rows(self, symbol: str, start_date: str, end_date: str) -> int:
        sym = normalize_symbol_key(symbol)
        row = self._conn.execute(
            """
            SELECT COUNT(*) FROM ohlcv
            WHERE symbol = ? AND date >= ? AND date <= ?
            """,
            [sym, start_date, end_date],
        ).fetchone()
        return int(row[0]) if row else 0


def chunk_date_ranges(
    start_date: str,
    end_date: str,
    max_days: int,
) -> List[tuple[str, str]]:
    """Split [start_date, end_date] into chunks of at most ``max_days`` calendar days."""
    from datetime import timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if start > end:
        return []

    chunks: List[tuple[str, str]] = []
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=max_days - 1), end)
        chunks.append((cur.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        cur = chunk_end + timedelta(days=1)
    return chunks


def trading_weekdays_in_range(dates: Iterable[str]) -> List[str]:
    """Filter YYYY-MM-DD strings to weekdays only."""
    out: List[str] = []
    for d in dates:
        try:
            dt = datetime.strptime(d.strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        if dt.weekday() < 5:
            out.append(dt.strftime("%Y-%m-%d"))
    return out
