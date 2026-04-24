"""Tests for backtest performance metrics (annualized return edge cases)."""

import json
import unittest

from tradingagents.backtest.ledger import PaperLedger
from tradingagents.backtest.metrics import annualized_return, compute_performance_stats


class TestBacktestMetrics(unittest.TestCase):
    def test_annualized_return_none_when_total_loss_exceeds_100_percent(self) -> None:
        """When 1 + total_return < 0, fractional real exponent is undefined as a real; return None."""
        rows = [
            {"date": "2020-01-01", "equity": 100_000.0, "close": 100.0},
            {"date": "2020-12-31", "equity": -50_000.0, "close": 100.0},
        ]
        tr = (rows[-1]["equity"] - 100_000.0) / 100_000.0
        self.assertLess(tr, -1.0)
        self.assertIsNone(annualized_return(tr, rows))

    def test_compute_performance_stats_json_safe_when_worse_than_total_loss(self) -> None:
        rows = [
            {"date": "2020-01-01", "equity": 100_000.0, "close": 100.0},
            {"date": "2020-12-31", "equity": -10_000.0, "close": 100.0},
        ]
        perf = compute_performance_stats(100_000.0, rows, PaperLedger(cash=0.0))
        self.assertIsNone(perf["annualized_return"])
        summary = {"annualized_return": perf["annualized_return"]}
        json.dumps(summary)

    def test_annualized_return_total_wipeout_is_real(self) -> None:
        """total_return == -1  => 1+r == 0; (0^*) - 1 is -1, real."""
        rows = [
            {"date": "2020-01-01", "equity": 100_000.0, "close": 100.0},
            {"date": "2020-12-31", "equity": 0.0, "close": 100.0},
        ]
        tr = -1.0
        ann = annualized_return(tr, rows)
        self.assertIsNotNone(ann)
        self.assertIsInstance(ann, float)
        self.assertEqual(ann, -1.0)


if __name__ == "__main__":
    unittest.main()
