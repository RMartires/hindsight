#!/usr/bin/env python3
"""Run the 10/50 SMA baseline on the frozen regime windows. No model calls.

Reads adjusted closes from the local DuckDB cache (same store as the agent
backtest) and writes one equity CSV plus a summary table under
``results/baselines/``.

Usage (from repo root):
  python scripts/rules_baseline.py
  python scripts/rules_baseline.py --db dataflows/data_cache/market.duckdb
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tradingagents.backtest.rules_baseline import (  # noqa: E402
    DEFAULT_FAST,
    DEFAULT_SLOW,
    PAPER_REGIME_WINDOWS,
    load_ohlcv_with_warmup,
    simulate_rules_baseline,
)


def _write_equity_csv(path: Path, result) -> None:
    fieldnames = [
        "date",
        "final_signal",
        "close",
        "cash",
        "shares",
        "equity",
        "fees_day",
        "cumulative_fees",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.equity_rows:
            writer.writerow({key: row[key] for key in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser(description="SMA crossover baseline on frozen regime windows")
    parser.add_argument("--fast", type=int, default=DEFAULT_FAST)
    parser.add_argument("--slow", type=int, default=DEFAULT_SLOW)
    parser.add_argument("--db", default="", help="Path to market.duckdb (default: configured cache)")
    parser.add_argument("--out", default="results/baselines", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for symbol, regime, start, end in PAPER_REGIME_WINDOWS:
        dates, closes, eval_idx = load_ohlcv_with_warmup(
            symbol,
            start,
            end,
            slow=args.slow,
            db_path=args.db or None,
        )
        result = simulate_rules_baseline(
            dates,
            closes,
            eval_start_idx=eval_idx,
            fast=args.fast,
            slow=args.slow,
        )
        stem = f"{symbol.replace('.', '_')}_{regime}_{start}_{end}"
        _write_equity_csv(out_dir / f"{stem}.csv", result)
        perf = result.performance
        summary_rows.append(
            {
                "symbol": symbol,
                "regime": regime,
                "start": start,
                "end": end,
                "n_days": len(result.dates),
                "warmup_bars": result.warmup_bars,
                "buys": result.signals.count("BUY"),
                "sells": result.signals.count("SELL"),
                "rules_net_return": perf["total_return"],
                "rules_max_drawdown": perf["max_drawdown"],
                "rules_fees": perf["total_transaction_costs"],
                "buy_and_hold_return": result.buy_and_hold_return,
                "alpha_vs_buy_and_hold": result.alpha_vs_buy_and_hold,
                "fast": args.fast,
                "slow": args.slow,
                "cost_model": perf["cost_model"],
            }
        )
        print(
            f"{symbol} {regime}: rules {perf['total_return']:+.2%}  "
            f"B&H {result.buy_and_hold_return:+.2%}  "
            f"alpha {result.alpha_vs_buy_and_hold:+.2%}  "
            f"MDD {perf['max_drawdown']:.2%}  "
            f"fees {perf['total_transaction_costs']:.2f}"
        )

    summary_path = out_dir / "sma_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    (out_dir / "sma_summary.json").write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"rules baseline: {exc}", file=sys.stderr)
        raise SystemExit(2)
