#!/usr/bin/env python3
"""
Prefetch daily OHLCV from Kite into local DuckDB for offline backtests.

Requires valid KITE_API_KEY and KITE_ACCESS_TOKEN (run kite_token_server.py first).

Usage (from repo root):
  python scripts/prefetch_market_data.py --ticker RELIANCE.NS --dates-csv results/dates.csv
  python scripts/prefetch_market_data.py --ticker RELIANCE.NS --start-date 2024-01-01 --end-date 2024-06-30
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_dotenv(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            os.environ.setdefault(key, value)


def _parse_dates(args: argparse.Namespace) -> list[str]:
    out: list[str] = []
    if args.dates:
        out.extend(d.strip() for d in args.dates.split(",") if d.strip())
    if args.dates_file:
        p = Path(args.dates_file)
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    if args.dates_csv:
        p = Path(args.dates_csv)
        if p.is_file():
            import csv

            with p.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames and "date" in reader.fieldnames:
                    for row in reader:
                        d = (row.get("date") or "").strip()
                        if d:
                            out.append(d)
                else:
                    for line in p.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            out.append(line.split(",")[0].strip())
    seen: set[str] = set()
    unique: list[str] = []
    for d in out:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def _resolve_fetch_range(
    dates: list[str],
    *,
    start_date: str | None,
    end_date: str | None,
    lookback_years: int,
) -> tuple[str, str, list[str]]:
    from dateutil.relativedelta import relativedelta

    from tradingagents.dataflows.local_db.store import trading_weekdays_in_range

    if dates:
        parsed = sorted(
            datetime.strptime(d[:10], "%Y-%m-%d").date() for d in dates
        )
        min_d = parsed[0]
        max_d = parsed[-1]
        trade_dates = trading_weekdays_in_range(dates)
    elif start_date and end_date:
        min_d = datetime.strptime(start_date, "%Y-%m-%d").date()
        max_d = datetime.strptime(end_date, "%Y-%m-%d").date()
        trade_dates = []
        cur = min_d
        while cur <= max_d:
            if cur.weekday() < 5:
                trade_dates.append(cur.strftime("%Y-%m-%d"))
            cur += timedelta(days=1)
    else:
        raise SystemExit("Provide --dates-csv, --dates/--dates-file, or --start-date and --end-date")

    ideal_start = min_d - relativedelta(years=lookback_years)
    fetch_start = ideal_start.strftime("%Y-%m-%d")
    fetch_end = max_d.strftime("%Y-%m-%d")
    return fetch_start, fetch_end, trade_dates


def prefetch_symbol(
    ticker: str,
    fetch_start: str,
    fetch_end: str,
    trade_dates: list[str],
    *,
    strict_coverage: bool,
) -> int:
    from tradingagents.dataflows.kite_common import KITE_HISTORICAL_MAX_INTERVAL_DAYS, is_kite_configured
    from tradingagents.dataflows.kite_ohlcv import fetch_kite_ohlcv_df
    from tradingagents.dataflows.local_db.store import (
        MarketDataStore,
        chunk_date_ranges,
        normalize_symbol_key,
    )

    if not is_kite_configured():
        raise SystemExit("Set KITE_API_KEY and KITE_ACCESS_TOKEN in .env before prefetch.")

    sym = normalize_symbol_key(ticker)
    chunks = chunk_date_ranges(fetch_start, fetch_end, KITE_HISTORICAL_MAX_INTERVAL_DAYS)
    print(f"Prefetch {sym}: {fetch_start} → {fetch_end} ({len(chunks)} Kite chunk(s))", file=sys.stderr)

    store = MarketDataStore()
    total_rows = 0
    try:
        for c_start, c_end in chunks:
            df = fetch_kite_ohlcv_df(sym, c_start, c_end)
            n = store.upsert_ohlcv_df(sym, df, source="kite")
            total_rows += n
            print(f"  chunk {c_start}–{c_end}: {n} rows upserted", file=sys.stderr)
    finally:
        store.close()

    print(f"Total rows upserted: {total_rows}", file=sys.stderr)
    print(f"DB path: {store.db_path}", file=sys.stderr)

    if trade_dates:
        store2 = MarketDataStore()
        try:
            present = store2.dates_present(sym, trade_dates)
        finally:
            store2.close()
        missing = [d for d in trade_dates if d not in present]
        print(
            f"Coverage: {len(present)}/{len(trade_dates)} backtest weekdays in DB",
            file=sys.stderr,
        )
        if missing:
            print(f"Missing dates ({len(missing)}): {missing[:10]}{'...' if len(missing) > 10 else ''}", file=sys.stderr)
            if strict_coverage:
                return 1
    return 0


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(description="Prefetch Kite OHLCV into local DuckDB.")
    parser.add_argument("--ticker", required=True, help="Symbol e.g. RELIANCE.NS")
    parser.add_argument("--dates", default="", help="Comma-separated YYYY-MM-DD")
    parser.add_argument("--dates-file", default="", help="File with one date per line")
    parser.add_argument("--dates-csv", default="", help="Backtest schedule CSV with date column")
    parser.add_argument("--start-date", default="", help="Range start YYYY-MM-DD")
    parser.add_argument("--end-date", default="", help="Range end YYYY-MM-DD")
    parser.add_argument(
        "--lookback-years",
        type=int,
        default=15,
        help="Years before min schedule date to fetch (default 15, for indicators)",
    )
    parser.add_argument(
        "--strict-coverage",
        action="store_true",
        default=True,
        help="Exit 1 if any backtest weekday missing from DB (default: on)",
    )
    parser.add_argument(
        "--no-strict-coverage",
        action="store_false",
        dest="strict_coverage",
        help="Allow partial coverage",
    )
    args = parser.parse_args()

    dates = _parse_dates(args)
    try:
        fetch_start, fetch_end, trade_dates = _resolve_fetch_range(
            dates,
            start_date=args.start_date.strip() or None,
            end_date=args.end_date.strip() or None,
            lookback_years=args.lookback_years,
        )
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2

    market_db = os.getenv("MARKET_DB_PATH", "").strip()
    if market_db:
        from tradingagents.dataflows.config import set_config

        set_config({"market_db_path": market_db})

    return prefetch_symbol(
        args.ticker,
        fetch_start,
        fetch_end,
        trade_dates,
        strict_coverage=args.strict_coverage,
    )


if __name__ == "__main__":
    raise SystemExit(main())
