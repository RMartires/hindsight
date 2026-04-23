"""Backtest performance metrics (single source of truth for runner + notebooks)."""

from __future__ import annotations

import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

from tradingagents.backtest.ledger import PaperLedger


def max_drawdown(equities: List[float]) -> float:
    if not equities:
        return 0.0
    peak = equities[0]
    max_dd = 0.0
    for x in equities:
        if x > peak:
            peak = x
        if peak > 0:
            dd = (peak - x) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd


def annualized_return(
    total_return: float,
    equity_rows: List[Dict[str, Any]],
) -> Optional[float]:
    if not equity_rows:
        return None
    d0 = equity_rows[0].get("date")
    d1 = equity_rows[-1].get("date")
    if not d0 or not d1:
        return None
    try:
        t0 = datetime.strptime(str(d0).strip(), "%Y-%m-%d")
        t1 = datetime.strptime(str(d1).strip(), "%Y-%m-%d")
    except ValueError:
        return None
    days = (t1 - t0).days
    if days <= 0:
        return None
    years = days / 365.25
    return (1.0 + total_return) ** (1.0 / years) - 1.0


def _daily_simple_returns(equity_rows: List[Dict[str, Any]]) -> List[float]:
    series: List[float] = []
    for r in equity_rows:
        v = r.get("equity")
        if v is None:
            continue
        try:
            series.append(float(v))
        except (TypeError, ValueError):
            continue
    if len(series) < 3:
        return []
    out: List[float] = []
    for i in range(1, len(series)):
        prev, cur = series[i - 1], series[i]
        if prev <= 0:
            continue
        out.append((cur / prev) - 1.0)
    return out


def sharpe_ratio(
    equity_rows: List[Dict[str, Any]],
    *,
    trading_days_per_year: float = 252.0,
) -> Optional[float]:
    returns = _daily_simple_returns(equity_rows)
    if len(returns) < 2:
        return None
    mean_r = statistics.mean(returns)
    try:
        std_r = statistics.stdev(returns)
    except statistics.StatisticsError:
        return None
    if std_r <= 1e-12:
        return None
    return (mean_r / std_r) * (trading_days_per_year**0.5)


def sortino_ratio(
    equity_rows: List[Dict[str, Any]],
    *,
    trading_days_per_year: float = 252.0,
    mar: float = 0.0,
) -> Optional[float]:
    """Sortino using downside deviation of daily simple returns vs ``mar`` (annualized)."""
    returns = _daily_simple_returns(equity_rows)
    if len(returns) < 2:
        return None
    mean_r = statistics.mean(returns)
    downside = [min(0.0, r - mar) ** 2 for r in returns]
    if not downside:
        return None
    ds = statistics.mean(downside) ** 0.5
    if ds <= 1e-12:
        return None
    return ((mean_r - mar) / ds) * (trading_days_per_year**0.5)


def calmar_ratio(
    total_return: float,
    equity_rows: List[Dict[str, Any]],
    *,
    max_dd: float,
) -> Optional[float]:
    """Annualized return divided by max drawdown (if drawdown > 0)."""
    ann = annualized_return(total_return, equity_rows)
    if ann is None or max_dd <= 1e-12:
        return None
    return float(ann) / float(max_dd)


def _equity_series_for_drawdown(equity_rows: List[Dict[str, Any]]) -> List[float]:
    equities = [float(r["equity"]) for r in equity_rows if r.get("close") is not None]
    if not equities and equity_rows:
        equities = [float(r["equity"]) for r in equity_rows]
    return equities


def gross_total_return(initial_cash: float, final_equity: float, cumulative_fees: float) -> float:
    """Return before fees: (final_equity + fees - initial) / initial."""
    ic = float(initial_cash)
    if ic <= 0:
        return 0.0
    return (float(final_equity) + float(cumulative_fees) - ic) / ic


def compute_performance_stats(
    initial_cash: float,
    equity_rows: List[Dict[str, Any]],
    ledger: PaperLedger,
) -> Dict[str, Any]:
    """Performance stats aligned with ``summary.json`` / schedule analysis."""
    total_fees = float(sum(t.fees_paid for t in ledger.trades))
    if not equity_rows:
        return {
            "total_return": 0.0,
            "gross_total_return": 0.0,
            "annualized_return": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "calmar_ratio": None,
            "max_drawdown": 0.0,
            "total_transaction_costs": total_fees,
            "cost_bps": float(ledger.cost_bps),
            "cost_model": str(getattr(ledger, "cost_model", "flat_bps") or "flat_bps"),
            "slippage_bps": float(getattr(ledger, "slippage_bps", 0.0)),
        }

    equities = _equity_series_for_drawdown(equity_rows)
    initial_eq = float(initial_cash)
    final_eq = float(equity_rows[-1]["equity"])
    total_return = (final_eq - initial_eq) / initial_eq if initial_eq else 0.0
    mdd = float(max_drawdown(equities)) if equities else 0.0
    ann = annualized_return(total_return, equity_rows)
    cal = calmar_ratio(total_return, equity_rows, max_dd=mdd)

    return {
        "total_return": total_return,
        "gross_total_return": gross_total_return(initial_cash, final_eq, total_fees),
        "annualized_return": ann,
        "sharpe_ratio": sharpe_ratio(equity_rows),
        "sortino_ratio": sortino_ratio(equity_rows),
        "calmar_ratio": cal,
        "max_drawdown": mdd,
        "total_transaction_costs": total_fees,
        "cost_bps": float(ledger.cost_bps),
        "cost_model": getattr(ledger, "cost_model", "flat_bps"),
        "slippage_bps": float(getattr(ledger, "slippage_bps", 0.0)),
    }


def buy_and_hold_total_return(
    initial_cash: float,
    first_close: float,
    last_close: float,
) -> Optional[float]:
    """Buy-and-hold on same capital: deploy all cash at first close, value at last close."""
    if first_close <= 0 or last_close <= 0:
        return None
    shares = float(initial_cash) / first_close
    final = shares * last_close
    return (final - float(initial_cash)) / float(initial_cash)
