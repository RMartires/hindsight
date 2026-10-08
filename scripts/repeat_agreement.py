#!/usr/bin/env python3
"""Repeat one ticker-day and score agreement of the parsed decision.

Each repeat builds a new graph, so debate memory from the previous repeat
does not enter the prompt. State logs go under the output directory and do
not overwrite ``eval_results/<ticker>/TradingAgentsStrategy_logs/``.

The pass line is modal share >= 0.80 on BUY/SELL/HOLD. ``proven_bar`` is true
only when the Wilson lower bound is also at least 0.80, which 10 runs cannot
reach unless every run agrees and N is about 20.

Usage (from repo root):
  python scripts/repeat_agreement.py --ticker TCS.NS --date 2024-06-03 --runs 10
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tradingagents.backtest.repeat_agreement import modal_agreement  # noqa: E402


def _backtest_helpers():
    """Load the paper backtest config without requiring ``scripts`` to be a package."""
    path = ROOT / "scripts" / "backtest_mvp.py"
    spec = importlib.util.spec_from_file_location("backtest_mvp", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._load_dotenv, module._build_config


def _one_decision(config: dict, ticker: str, trade_date: str, log_dir: Path) -> str:
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    cfg = copy.deepcopy(config)
    cfg["state_log_dir"] = str(log_dir)
    graph = TradingAgentsGraph(
        debug=False,
        config=cfg,
        selected_analysts=list(cfg.get("selected_analysts") or []),
    )
    _state, processed = graph.propagate(ticker, trade_date, use_live_portfolio=False)
    token = str(processed or "").strip().upper()
    if token not in ("BUY", "SELL", "HOLD"):
        raise RuntimeError(f"decision was {processed!r}, expected BUY, SELL, or HOLD")
    return token


def main() -> int:
    load_dotenv, build_config = _backtest_helpers()
    load_dotenv()
    parser = argparse.ArgumentParser(description="Same-input decision agreement for one ticker-day")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--bar", type=float, default=0.80)
    parser.add_argument(
        "--out",
        default="",
        help="Output directory (default: results/repeat_agreement/<ticker>/<date>)",
    )
    args = parser.parse_args()
    if args.runs < 2:
        logging.error("--runs must be at least 2")
        return 2

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        config = build_config()
    except ValueError as exc:
        logging.error("%s", exc)
        return 2

    ticker = args.ticker.strip()
    out = Path(args.out) if args.out else Path("results/repeat_agreement") / ticker / args.date
    out.mkdir(parents=True, exist_ok=True)

    labels: list[str] = []
    rows: list[dict[str, object]] = []
    for i in range(1, args.runs + 1):
        run_dir = out / f"run-{i:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        logging.info("repeat %s/%s %s %s", i, args.runs, ticker, args.date)
        try:
            label = _one_decision(config, ticker, args.date, run_dir)
            error = ""
        except Exception as exc:
            label = "ERROR"
            error = str(exc)
            logging.exception("repeat %s failed", i)
        labels.append(label)
        rows.append({"run": i, "label": label, "error": error})
        (out / "repeats.json").write_text(
            json.dumps(rows, indent=2) + "\n",
            encoding="utf-8",
        )

    score = modal_agreement(labels, bar=args.bar)
    payload = {
        "ticker": ticker,
        "date": args.date,
        "repeats": rows,
        "agreement": score.as_dict(),
    }
    summary = out / "agreement.json"
    summary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    counts = ", ".join(f"{name} {count}" for name, count in sorted(score.counts.items()))
    print(
        f"mode={score.mode or 'tie'} share={score.modal_share:.1%} "
        f"wilson=[{score.wilson_low:.1%}, {score.wilson_high:.1%}] "
        f"passes_{score.bar:.0%}={score.passes_bar} proven={score.proven_bar}"
    )
    print(f"counts: {counts}")
    print(f"wrote {summary}")
    return 0 if score.passes_bar else 1


if __name__ == "__main__":
    raise SystemExit(main())
