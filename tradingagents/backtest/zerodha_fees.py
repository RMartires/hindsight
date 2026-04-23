"""Zerodha (Kite) equity fee estimates for paper backtests.

Rates are sourced from https://zerodha.com/charge-list (equity, NSE) as of implementation;
verify before production use — statutory rates change.

This module returns **total INR charges per trade leg** (buy or sell), not brokerage alone.
"""

from __future__ import annotations

# Reference: Zerodha charge list — equity delivery / intraday (NSE)
ZERODHA_CHARGE_LIST_URL = "https://zerodha.com/charge-list"

# ₹10 per crore notional → rupees per rupee of turnover
SEBI_PER_INR = 10.0 / 10_000_000.0

NSE_TXN_RATE_DELIVERY = 0.0000307  # 0.00307%
NSE_TXN_RATE_INTRADAY = 0.0000307

STT_DELIVERY = 0.001  # 0.1% on buy and on sell
STT_INTRADAY_SELL = 0.00025  # 0.025% sell only

STAMP_DELIVERY_BUY = 0.00015  # 0.015% on buy (equity delivery)
STAMP_INTRADAY_BUY = 0.00003  # 0.003% on buy (equity intraday)

BROKERAGE_INTRADAY_PCT = 0.0003  # 0.03%
BROKERAGE_INTRADAY_CAP_INR = 20.0

# DP charge when selling delivery (flat per sell transaction; CDSL + Zerodha + GST bundled ~₹15.34 on site)
DP_CHARGE_DELIVERY_SELL_INR = 15.34

GST_RATE = 0.18


def _gst_on_service_base(brokerage: float, sebi: float, txn: float) -> float:
    return GST_RATE * (brokerage + sebi + txn)


def zerodha_fees_buy_delivery_inr(notional: float) -> float:
    """Statutory + exchange costs on a **delivery** buy (INR turnover = cash deployed for stock)."""
    if notional <= 0:
        return 0.0
    brokerage = 0.0
    stt = STT_DELIVERY * notional
    txn = NSE_TXN_RATE_DELIVERY * notional
    stamp = STAMP_DELIVERY_BUY * notional
    sebi = SEBI_PER_INR * notional
    gst = _gst_on_service_base(brokerage, sebi, txn)
    return stt + txn + stamp + sebi + gst


def zerodha_fees_sell_delivery_inr(notional: float) -> float:
    """Delivery sell: STT, txn, SEBI, GST, flat DP (no stamp on sell per Zerodha delivery table)."""
    if notional <= 0:
        return 0.0
    brokerage = 0.0
    stt = STT_DELIVERY * notional
    txn = NSE_TXN_RATE_DELIVERY * notional
    sebi = SEBI_PER_INR * notional
    gst = _gst_on_service_base(brokerage, sebi, txn)
    return stt + txn + sebi + gst + DP_CHARGE_DELIVERY_SELL_INR


def zerodha_fees_buy_intraday_inr(notional: float) -> float:
    if notional <= 0:
        return 0.0
    brokerage = min(BROKERAGE_INTRADAY_PCT * notional, BROKERAGE_INTRADAY_CAP_INR)
    stt = 0.0  # intraday equity STT on sell only
    txn = NSE_TXN_RATE_INTRADAY * notional
    stamp = STAMP_INTRADAY_BUY * notional
    sebi = SEBI_PER_INR * notional
    gst = _gst_on_service_base(brokerage, sebi, txn)
    return brokerage + stt + txn + stamp + sebi + gst


def zerodha_fees_sell_intraday_inr(notional: float) -> float:
    if notional <= 0:
        return 0.0
    brokerage = min(BROKERAGE_INTRADAY_PCT * notional, BROKERAGE_INTRADAY_CAP_INR)
    stt = STT_INTRADAY_SELL * notional
    txn = NSE_TXN_RATE_INTRADAY * notional
    sebi = SEBI_PER_INR * notional
    gst = _gst_on_service_base(brokerage, sebi, txn)
    return brokerage + stt + txn + sebi + gst


def fees_for_leg_inr(
    *,
    cost_model: str,
    side: str,
    notional_inr: float,
) -> float:
    """Total fees in INR for one BUY or SELL leg."""
    n = max(0.0, float(notional_inr))
    cm = (cost_model or "flat_bps").strip().lower()
    if cm == "zerodha_delivery":
        return (
            zerodha_fees_buy_delivery_inr(n) if side == "BUY" else zerodha_fees_sell_delivery_inr(n)
        )
    if cm == "zerodha_intraday":
        return (
            zerodha_fees_buy_intraday_inr(n) if side == "BUY" else zerodha_fees_sell_intraday_inr(n)
        )
    return 0.0


def slippage_cost_inr(notional_inr: float, slippage_bps: float) -> float:
    if notional_inr <= 0:
        return 0.0
    return float(notional_inr) * max(0.0, float(slippage_bps)) / 10_000.0
