"""SMA baseline: position changes, fees, and no lookahead. No market data required."""

import unittest

from tradingagents.backtest.rules_baseline import (
    simple_moving_average,
    simulate_rules_baseline,
    sma_position_signals,
)


def _trend(n: int, start: float, step: float) -> list[float]:
    return [start + step * i for i in range(n)]


class TestSmaSignals(unittest.TestCase):
    def test_sma_matches_hand_average(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(simple_moving_average(values, 2), [None, 1.5, 2.5, 3.5])

    def test_uptrend_buys_once_then_holds(self) -> None:
        closes = _trend(30, 100.0, 1.0)
        signals = sma_position_signals(closes, 0, fast=3, slow=5)
        self.assertEqual(signals.count("BUY"), 1)
        self.assertEqual(signals.count("SELL"), 0)
        self.assertEqual(signals[0], "HOLD")  # slow SMA not ready
        self.assertIn("BUY", signals)

    def test_downtrend_stays_flat(self) -> None:
        closes = _trend(30, 200.0, -1.0)
        signals = sma_position_signals(closes, 0, fast=3, slow=5)
        self.assertEqual(signals, ["HOLD"] * len(closes))

    def test_fast_must_be_shorter_than_slow(self) -> None:
        with self.assertRaises(ValueError):
            sma_position_signals([1.0, 2.0, 3.0], 0, fast=5, slow=5)

    def test_warmup_does_not_trade_before_the_window(self) -> None:
        # Rise through the warmup, then fall inside the window: one sell, no buy
        # if the book starts flat and the window opens already long... it should BUY
        # on day 0 of the window because the state is long, using warmup only for the SMA.
        rise = _trend(10, 100.0, 1.0)
        fall = _trend(8, rise[-1] - 1.0, -3.0)
        closes = rise + fall
        signals = sma_position_signals(closes, len(rise), fast=3, slow=5)
        self.assertEqual(len(signals), len(fall))
        self.assertEqual(signals[0], "BUY")
        self.assertIn("SELL", signals)


class TestSimulateRulesBaseline(unittest.TestCase):
    def test_uptrend_is_long_and_pays_one_buy_fee(self) -> None:
        closes = _trend(40, 100.0, 1.0)
        dates = [f"2024-01-{i+1:02d}" for i in range(len(closes))]
        result = simulate_rules_baseline(
            dates,
            closes,
            fast=3,
            slow=5,
            initial_cash=10_000.0,
            cost_model="flat_bps",
            cost_bps=0.0,
        )
        self.assertEqual(result.signals.count("BUY"), 1)
        self.assertEqual(result.signals.count("SELL"), 0)
        self.assertGreater(result.performance["total_return"], 0.0)
        self.assertAlmostEqual(result.performance["total_transaction_costs"], 0.0)
        self.assertIsNotNone(result.alpha_vs_buy_and_hold)
        # Entered after the slow SMA exists, so the rule lags buy-and-hold.
        self.assertLess(result.performance["total_return"], result.buy_and_hold_return)

    def test_signal_ignores_future_closes(self) -> None:
        closes = _trend(20, 50.0, 0.5)
        dates = [f"2024-03-{i+1:02d}" for i in range(len(closes))]
        full = simulate_rules_baseline(dates, closes, fast=2, slow=4, cost_bps=0.0)
        truncated = simulate_rules_baseline(
            dates[:12],
            closes[:12],
            fast=2,
            slow=4,
            cost_bps=0.0,
        )
        self.assertEqual(full.signals[:12], truncated.signals)


if __name__ == "__main__":
    unittest.main()
