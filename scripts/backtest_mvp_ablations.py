#!/usr/bin/env python3
"""
Run ``backtest_mvp`` over a date range for every ``PAPER_ABLATION`` preset (a1, a2, a3, full).

Writes one CSV per (ablation, date range, ticker) under ``results/``, using the same columns as
``equity.csv`` from :func:`tradingagents.backtest.runner.run_backtest_mvp`.

By default, if a CSV already exists and its ``date`` column matches the **leading** weekdays of the
requested range, the run **continues from the next missing day** (using cash/shares from the last
row). If the file already contains every weekday in range, that ablation is skipped. Mismatched or
longer files trigger a full rerender of that ablation. Use CLI ``--no-resume`` (or ``"resume":
False`` in ``INLINE_PARAMS``) to always overwrite.

Usage (from repo root):
  .venv/bin/python scripts/backtest_mvp_ablations.py --ticker RELIANCE.NS --start-date 2024-05-01 --end-date 2024-05-31

Or set ``USE_INLINE_PARAMS`` below to ``True`` and edit ``INLINE_PARAMS``; then run the script with no arguments.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import logging
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from tradingagents.backtest.ledger import PaperLedger

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -----------------------------------------------------------------------------
# Quick run without CLI: set to True and fill INLINE_PARAMS (CLI is ignored).
# -----------------------------------------------------------------------------
USE_INLINE_PARAMS = True
INLINE_PARAMS: dict[str, Any] = {
    "ticker": "RELIANCE.NS",
    "start_date": "2024-05-01",
    "end_date": "2024-06-30",
    "initial_cash": 100_000.0,
    "buy_fraction": 1.0,
    "cost_bps": None,
    "use_llm_signal": False,
    "debug": False,
    "results_dir": None,
    # True: reuse existing output CSV rows as a prefix when dates match; continue remaining weekdays.
    "resume": True,
}


def _load_backtest_mvp_cli():
    path = ROOT / "scripts" / "backtest_mvp.py"
    spec = importlib.util.spec_from_file_location("backtest_mvp_cli", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_bt = _load_backtest_mvp_cli()
_load_dotenv = _bt._load_dotenv
_build_config = _bt._build_config

from cli.stats_handler import StatsCallbackHandler
from tradingagents.backtest.runner import run_backtest_mvp
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.observability.langfuse_config import get_langfuse_client, get_langfuse_handler
from tradingagents.paper_ablation import PAPER_ABLATION_LABELS


def _parse_ymd(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def _weekdays_inclusive(start: date, end: date) -> list[str]:
    if start > end:
        raise ValueError(f"start date {start} is after end date {end}")
    out: list[str] = []
    d = start
    delta = timedelta(days=1)
    while d <= end:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += delta
    return out


def _safe_ticker_for_filename(ticker: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in ticker.strip())


def _last_valid_close(rows: list[dict[str, Any]]) -> float | None:
    for r in reversed(rows):
        c = r.get("close")
        if c is None:
            continue
        s = str(c).strip()
        if not s:
            continue
        try:
            return float(s)
        except ValueError:
            continue
    return None


@dataclass
class _ResumePlan:
    prepend_rows: list[dict[str, Any]]
    remaining_dates: list[str]
    initial_ledger: PaperLedger
    initial_last_close: float | None


def _inspect_csv_for_resume(
    dest_csv: Path,
    full_dates: list[str],
    *,
    cost_bps: float,
    cost_model: str,
    slippage_bps: float,
    resume_enabled: bool,
) -> tuple[bool, _ResumePlan | None]:
    """Return (already_complete_skip, resume_plan_or_none).

    If ``already_complete_skip``, this ablation has a CSV with all ``full_dates``; do not run again.
    If ``resume_plan_or_none`` is None (and not skip), run the full weekday list from scratch.
    Otherwise run only ``resume_plan.remaining_dates`` with prepended ledger state.
    """
    if not resume_enabled or not dest_csv.is_file():
        return False, None
    try:
        with dest_csv.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as e:
        logging.warning("Could not read %s (%s); will rerun full range", dest_csv, e)
        return False, None
    if not rows:
        return False, None
    seen_dates = [str(r.get("date", "") or "").strip() for r in rows]
    n = len(seen_dates)
    if any(not d for d in seen_dates):
        logging.warning("%s has blank date rows; will rerun full range", dest_csv)
        return False, None
    if n > len(full_dates):
        logging.warning("%s has more rows than schedule; will rerun full range", dest_csv)
        return False, None
    if seen_dates != full_dates[:n]:
        logging.warning(
            "%s row dates do not match the weekday prefix %s …; will rerun full range",
            dest_csv,
            full_dates[0] if full_dates else "",
        )
        return False, None
    if n == len(full_dates):
        logging.info("%s already has all %s weekdays — skipping run", dest_csv, n)
        return True, None
    last = rows[-1]
    try:
        cash = float(str(last.get("cash", "")).strip() or "nan")
        shares = float(str(last.get("shares", "")).strip() or "nan")
    except (TypeError, ValueError):
        logging.warning("%s last row has invalid cash/shares; will rerun full range", dest_csv)
        return False, None
    if cash != cash or shares != shares:  # NaN
        logging.warning("%s last row has non-numeric cash/shares; will rerun full range", dest_csv)
        return False, None
    ledger = PaperLedger(
        cash=cash,
        shares=shares,
        cost_bps=float(cost_bps),
        cost_model=str(cost_model or "flat_bps"),
        slippage_bps=float(slippage_bps),
    )
    last_close = _last_valid_close(rows)
    remaining = full_dates[n:]
    plan = _ResumePlan(
        prepend_rows=rows,
        remaining_dates=remaining,
        initial_ledger=ledger,
        initial_last_close=last_close,
    )
    logging.info(
        "Resume %s from %s (%s days done; %s left)",
        dest_csv.name,
        remaining[0] if remaining else "",
        n,
        len(remaining),
    )
    return False, plan


def _peek_cost_for_resume(ablation: str, cost_bps_override: float | None) -> tuple[float, str, float]:
    """Ledger fee params consistent with `_run_one_ablation` for resume reconstruction."""
    prev = os.environ.get("PAPER_ABLATION")
    os.environ["PAPER_ABLATION"] = ablation
    try:
        config = _build_config()
    finally:
        if prev is None:
            os.environ.pop("PAPER_ABLATION", None)
        else:
            os.environ["PAPER_ABLATION"] = prev
    cost_bps_eff = float(config.get("backtest_cost_bps", 0) or 0)
    if cost_bps_override is not None:
        cost_bps_eff = float(cost_bps_override)
    cost_model = str(config.get("backtest_cost_model", "flat_bps") or "flat_bps")
    slippage_bps = float(config.get("backtest_slippage_bps", 0) or 0)
    return cost_bps_eff, cost_model, slippage_bps


def _run_ablation_grid(
    *,
    ticker: str,
    start_date: str,
    end_date: str,
    initial_cash: float,
    buy_fraction: float,
    cost_bps: float | None,
    use_llm_signal: bool,
    debug: bool,
    results_dir: Path | None,
    resume_enabled: bool = True,
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    try:
        start_d = _parse_ymd(start_date)
        end_d = _parse_ymd(end_date)
    except ValueError as e:
        logging.error("Invalid start/end date (use YYYY-MM-DD): %s", e)
        return 2

    try:
        dates = _weekdays_inclusive(start_d, end_d)
    except ValueError as e:
        logging.error("%s", e)
        return 2

    if not dates:
        logging.error("No weekdays in range %s .. %s", start_date, end_date)
        return 2

    results_base = (results_dir if results_dir is not None else ROOT / "results").resolve()
    ticker = ticker.strip()
    t_safe = _safe_ticker_for_filename(ticker)
    start_s = start_d.isoformat()
    end_s = end_d.isoformat()

    for ablation in sorted(PAPER_ABLATION_LABELS):
        dest = results_base / f"{ablation}_{start_s}_{end_s}_{t_safe}.csv"
        staging = results_base / f".staging_{ablation}_{start_s}_{end_s}_{t_safe}"
        cfg_probe = _peek_cost_for_resume(ablation, cost_bps)
        skip_done, resume_plan = _inspect_csv_for_resume(
            dest,
            dates,
            cost_bps=cfg_probe[0],
            cost_model=cfg_probe[1],
            slippage_bps=cfg_probe[2],
            resume_enabled=resume_enabled,
        )
        if skip_done:
            continue
        ndays_run = len(resume_plan.remaining_dates) if resume_plan else len(dates)
        logging.info(
            "Running ablation=%s ticker=%s weekdays=%s%s -> %s",
            ablation,
            ticker,
            ndays_run,
            f" (resume, {len(dates)} total schedule)" if resume_plan else "",
            dest,
        )
        try:
            _run_one_ablation(
                ablation=ablation,
                ticker=ticker,
                schedule_dates=dates,
                resume_plan=resume_plan,
                initial_cash=initial_cash,
                buy_fraction=buy_fraction,
                cost_bps=cost_bps,
                use_llm_signal=use_llm_signal,
                debug=debug,
                dest_csv=dest,
                staging_dir=staging,
            )
        except Exception:
            logging.exception("Ablation %s failed", ablation)
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            return 1

    logging.info("All ablations finished; outputs under %s", results_base)
    return 0


def _run_one_ablation(
    *,
    ablation: str,
    ticker: str,
    schedule_dates: list[str],
    resume_plan: _ResumePlan | None,
    initial_cash: float,
    buy_fraction: float,
    cost_bps: float | None,
    use_llm_signal: bool,
    debug: bool,
    dest_csv: Path,
    staging_dir: Path,
) -> None:
    prev = os.environ.get("PAPER_ABLATION")
    os.environ["PAPER_ABLATION"] = ablation
    try:
        config = _build_config()
    finally:
        if prev is None:
            os.environ.pop("PAPER_ABLATION", None)
        else:
            os.environ["PAPER_ABLATION"] = prev

    cost_bps_eff = float(config.get("backtest_cost_bps", 0) or 0)
    if cost_bps is not None:
        cost_bps_eff = float(cost_bps)
    cost_model = str(config.get("backtest_cost_model", "flat_bps") or "flat_bps")
    slippage_bps = float(config.get("backtest_slippage_bps", 0) or 0)

    stats_handler = StatsCallbackHandler()
    callbacks = [stats_handler]
    langfuse_handler = get_langfuse_handler() if get_langfuse_client() is not None else None
    if langfuse_handler is not None:
        callbacks.append(langfuse_handler)

    graph = TradingAgentsGraph(
        debug=debug,
        config=config,
        callbacks=callbacks,
        selected_analysts=list(config.get("selected_analysts") or []),
    )

    langfuse_meta = {
        "llm_provider": config.get("llm_provider"),
        "quick_think_llm": config.get("quick_think_llm"),
        "deep_think_llm": config.get("deep_think_llm"),
    }

    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    dest_csv.parent.mkdir(parents=True, exist_ok=True)

    def _mirror_equity_to_dest(equity_path: Path) -> None:
        shutil.copy2(equity_path, dest_csv)

    dates_run = resume_plan.remaining_dates if resume_plan else schedule_dates
    if not dates_run:
        logging.warning("No remaining dates for %s (%s)", ablation, dest_csv)
        return

    out = run_backtest_mvp(
        graph,
        ticker,
        dates_run,
        initial_cash=initial_cash,
        buy_fraction=buy_fraction,
        cost_bps=cost_bps_eff,
        cost_model=cost_model,
        slippage_bps=slippage_bps,
        use_llm_signal=use_llm_signal,
        results_dir=staging_dir,
        use_live_portfolio=False,
        langfuse_meta=langfuse_meta,
        on_day_complete=None,
        on_equity_csv_written=_mirror_equity_to_dest,
        langfuse_dates_total=len(schedule_dates),
        initial_ledger=resume_plan.initial_ledger if resume_plan else None,
        initial_last_close=(resume_plan.initial_last_close if resume_plan else None),
        prepend_equity_rows=resume_plan.prepend_rows if resume_plan else None,
        total_trading_days=len(schedule_dates),
    )

    equity_csv = staging_dir / "equity.csv"
    if not equity_csv.is_file():
        raise FileNotFoundError(f"Expected {equity_csv} after backtest")
    shutil.rmtree(staging_dir)

    s = out["summary"]
    logging.info(
        "Wrote %s (ablation=%s final_equity=%.2f total_return=%.4f)",
        dest_csv,
        ablation,
        s["final_equity"],
        s["total_return"],
    )


def main() -> int:
    _load_dotenv()

    if USE_INLINE_PARAMS:
        p = INLINE_PARAMS
        ticker = str(p.get("ticker") or "").strip()
        start_date = str(p.get("start_date") or "").strip()
        end_date = str(p.get("end_date") or "").strip()
        if not ticker or not start_date or not end_date:
            logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
            logging.error(
                "USE_INLINE_PARAMS is True but ticker/start_date/end_date must be non-empty in INLINE_PARAMS"
            )
            return 2
        rd = p.get("results_dir")
        results_path = Path(rd).resolve() if rd else None
        return _run_ablation_grid(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_cash=float(p.get("initial_cash", 100_000.0)),
            buy_fraction=float(p.get("buy_fraction", 1.0)),
            cost_bps=p.get("cost_bps"),
            use_llm_signal=bool(p.get("use_llm_signal", False)),
            debug=bool(p.get("debug", False)),
            results_dir=results_path,
            resume_enabled=bool(p.get("resume", True)),
        )

    parser = argparse.ArgumentParser(
        description="Backtest MVP for all PAPER_ABLATION presets; save equity CSVs under results/"
    )
    parser.add_argument("--ticker", required=True, help="Single symbol (e.g. RELIANCE or RELIANCE.NS)")
    parser.add_argument("--start-date", required=True, help="First calendar day (YYYY-MM-DD), inclusive")
    parser.add_argument(
        "--end-date",
        "--stop-date",
        required=True,
        dest="end_date",
        metavar="END_DATE",
        help="Last calendar day (YYYY-MM-DD), inclusive; weekends are skipped as trading days",
    )
    parser.add_argument("--initial-cash", type=float, default=100_000.0)
    parser.add_argument("--buy-fraction", type=float, default=1.0)
    parser.add_argument(
        "--cost-bps",
        type=float,
        default=None,
        help="Override transaction cost in bps (else env / config)",
    )
    parser.add_argument("--use-llm-signal", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=None,
        help=f"Directory for output CSVs (default: {ROOT / 'results'})",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Always recompute the full date range and overwrite CSVs (default: reuse partial CSV prefixes)",
    )
    args = parser.parse_args()

    return _run_ablation_grid(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_cash=args.initial_cash,
        buy_fraction=args.buy_fraction,
        cost_bps=args.cost_bps,
        use_llm_signal=args.use_llm_signal,
        debug=args.debug,
        results_dir=args.results_dir,
        resume_enabled=not args.no_resume,
    )


if __name__ == "__main__":
    raise SystemExit(main())
