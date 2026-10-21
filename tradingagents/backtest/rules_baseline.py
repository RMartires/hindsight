"""Non-LLM price rules for the paper backtest. No model calls.

The default rule is a 10/50 simple-moving-average state rule: be long when the
fast average is above the slow average, otherwise flat. Signals use only closes
through the decision day. The book starts in cash on the first day of the
evaluation window (same as the agent runs). History before that window is used
only to warm the averages.

Costs match Frozen E1: ``zerodha_delivery``, zero slippage, INR 100,000 start.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

from tradingagents.backtest.ledger import PaperLedger
from tradingagents.backtest.metrics import buy_and_hold_total_return, compute_performance_stats

DEFAULT_FAST = 10
DEFAULT_SLOW = 50
DEFAULT_INITIAL_CASH = 100_000.0
DEFAULT_COST_MODEL = "zerodha_delivery"

# Frozen E1 windows from regime-timeranges / manuscript Table of windows.
PAPER_REGIME_WINDOWS: Tuple[Tuple[str, str, str, str], ...] = (
    ("RELIANCE.NS", "bear", "2024-08-01", "2025-01-03"),
    ("RELIANCE.NS", "bull", "2025-01-01", "2025-06-03"),
    ("TCS.NS", "bull", "2024-06-03", "2024-09-03"),
    ("TCS.NS", "bear", "2024-12-02", "2025-04-03"),
)


def simple_moving_average(values: Sequence[float], window: int) -> List[Optional[float]]:
    """SMA aligned to ``values``. Entries before ``window`` observations are None."""
    if window < 1:
        raise ValueError("window must be >= 1")
    out: List[Optional[float]] = [None] * len(values)
    acc = 0.0
    for i, value in enumerate(values):
        acc += float(value)
        if i >= window:
            acc -= float(values[i - window])
        if i >= window - 1:
            out[i] = acc / window
    return out


def sma_position_signals(
    closes: Sequence[float],
    eval_start_idx: int,
    *,
    fast: int = DEFAULT_FAST,
    slow: int = DEFAULT_SLOW,
) -> List[str]:
    """BUY/SELL/HOLD for ``closes[eval_start_idx:]``.

    Long when fast SMA > slow SMA. BUY and SELL fire only when the target
    position changes, so a persistent trend does not pay a fee every day.
    The book is flat at the start of the evaluation window.
    """
    if fast < 1 or slow < 1:
        raise ValueError("SMA windows must be >= 1")
    if fast >= slow:
        raise ValueError("fast window must be shorter than slow window")
    if eval_start_idx < 0 or eval_start_idx > len(closes):
        raise ValueError("eval_start_idx out of range")

    fast_sma = simple_moving_average(closes, fast)
    slow_sma = simple_moving_average(closes, slow)
    signals: List[str] = []
    long = False
    for i in range(eval_start_idx, len(closes)):
        fast_value = fast_sma[i]
        slow_value = slow_sma[i]
        if fast_value is None or slow_value is None:
            signals.append("HOLD")
            continue
        want_long = fast_value > slow_value
        if want_long and not long:
            signals.append("BUY")
            long = True
        elif not want_long and long:
            signals.append("SELL")
            long = False
        else:
            signals.append("HOLD")
    return signals


@dataclass
class RulesBaselineResult:
    dates: List[str]
    closes: List[float]
    signals: List[str]
    equity_rows: List[Dict[str, Any]]
    performance: Dict[str, Any]
    buy_and_hold_return: Optional[float]
    fast: int
    slow: int
    warmup_bars: int

    @property
    def alpha_vs_buy_and_hold(self) -> Optional[float]:
        if self.buy_and_hold_return is None:
            return None
        return float(self.performance["total_return"]) - float(self.buy_and_hold_return)


def simulate_rules_baseline(
    dates: Sequence[str],
    closes: Sequence[float],
    *,
    eval_start_idx: int = 0,
    fast: int = DEFAULT_FAST,
    slow: int = DEFAULT_SLOW,
    initial_cash: float = DEFAULT_INITIAL_CASH,
    cost_model: str = DEFAULT_COST_MODEL,
    cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
    buy_fraction: float = 1.0,
) -> RulesBaselineResult:
    """Run the SMA rule on one window and score it with the paper ledger."""
    if len(dates) != len(closes):
        raise ValueError("dates and closes must have the same length")
    if not dates:
        raise ValueError("no bars")

    signals = sma_position_signals(closes, eval_start_idx, fast=fast, slow=slow)
    eval_dates = list(dates[eval_start_idx:])
    eval_closes = [float(c) for c in closes[eval_start_idx:]]
    if len(signals) != len(eval_dates):
        raise RuntimeError("signal length does not match evaluation window")

    ledger = PaperLedger(
        cash=float(initial_cash),
        cost_bps=float(cost_bps),
        cost_model=cost_model,
        slippage_bps=float(slippage_bps),
    )
    equity_rows: List[Dict[str, Any]] = []
    for trade_date, close, signal in zip(eval_dates, eval_closes, signals):
        if close <= 0:
            raise ValueError(f"non-positive close on {trade_date}")
        ledger.apply_signal(signal, close, buy_fraction=buy_fraction, asof_date=trade_date)
        fees_day = float(ledger.trades[-1].fees_paid) if ledger.trades else 0.0
        cumulative = float(sum(t.fees_paid for t in ledger.trades))
        equity_rows.append(
            {
                "date": trade_date,
                "final_signal": signal,
                "close": close,
                "cash": ledger.cash,
                "shares": ledger.shares,
                "equity": ledger.equity(close),
                "fees_day": fees_day,
                "cumulative_fees": cumulative,
            }
        )

    performance = compute_performance_stats(float(initial_cash), equity_rows, ledger)
    bh = buy_and_hold_total_return(float(initial_cash), eval_closes[0], eval_closes[-1])
    return RulesBaselineResult(
        dates=eval_dates,
        closes=eval_closes,
        signals=signals,
        equity_rows=equity_rows,
        performance=performance,
        buy_and_hold_return=bh,
        fast=fast,
        slow=slow,
        warmup_bars=eval_start_idx,
    )


def _as_date(value: Any) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]


def load_ohlcv_with_warmup(
    symbol: str,
    start_date: str,
    end_date: str,
    *,
    slow: int = DEFAULT_SLOW,
    db_path: Optional[str] = None,
) -> Tuple[List[str], List[float], int]:
    """Load adjusted closes from DuckDB, including bars before ``start_date``.

    Returns ``(dates, adj_closes, eval_start_idx)``. Raises ``FileNotFoundError``
    when the cache is missing and ``ValueError`` when the slow SMA cannot be
    computed on the first day of the window.
    """
    from tradingagents.dataflows.local_db.store import MarketDataStore, resolve_market_db_path

    path = db_path or resolve_market_db_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"No market database at {path}. Prefetch OHLCV before running the rules baseline."
        )

    start = datetime.strptime(start_date, "%Y-%m-%d")
    # Calendar buffer so ``slow`` trading days fit before the window (weekends, holidays).
    lookback_start = (start - timedelta(days=max(slow * 3, 180))).strftime("%Y-%m-%d")
    store = MarketDataStore(db_path=path, read_only=True)
    try:
        frame = store.load_ohlcv_df(symbol, lookback_start, end_date)
    finally:
        store.close()

    if frame.empty:
        raise ValueError(f"No OHLCV for {symbol} between {lookback_start} and {end_date}")

    dates = [_as_date(d) for d in frame["Date"]]
    closes = [float(c) for c in frame["Adj Close"]]
    eval_idx = next((i for i, d in enumerate(dates) if d >= start_date), None)
    if eval_idx is None:
        raise ValueError(f"No bars for {symbol} on or after {start_date}")
    in_window = [d for d in dates[eval_idx:] if d <= end_date]
    if not in_window:
        raise ValueError(f"No bars for {symbol} inside {start_date} .. {end_date}")
    # Trim anything after the window end.
    end_offset = next((i for i, d in enumerate(dates) if d > end_date), len(dates))
    dates = dates[:end_offset]
    closes = closes[:end_offset]
    if eval_idx < slow - 1:
        raise ValueError(
            f"{symbol} has {eval_idx} bars before {start_date}; "
            f"the {slow}-day SMA needs {slow - 1}. Prefetch earlier history."
        )
    return dates, closes, eval_idx
