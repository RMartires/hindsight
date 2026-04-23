"""Tests for simulation date clamping (no lookahead in backtests)."""

import unittest

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.simulation_context import (
    clamp_date_range,
    clamp_date_str,
    effective_data_end_date,
    effective_simulation_end_date_str,
)


class TestSimulationTemporal(unittest.TestCase):
    def tearDown(self) -> None:
        set_config({"simulation_data_end": None})

    def test_effective_end_prior_day(self) -> None:
        set_config({"simulation_data_end_policy": "prior_calendar_day"})
        self.assertEqual(effective_simulation_end_date_str("2020-06-15"), "2020-06-14")

    def test_effective_end_trade_date(self) -> None:
        set_config({"simulation_data_end_policy": "trade_date"})
        self.assertEqual(effective_simulation_end_date_str("2020-06-15"), "2020-06-15")

    def test_clamp_when_cap_set(self) -> None:
        set_config({"simulation_data_end": "2020-01-10"})
        self.assertEqual(effective_data_end_date(), "2020-01-10")
        self.assertEqual(clamp_date_str("2020-01-05"), "2020-01-05")
        self.assertEqual(clamp_date_str("2020-12-31"), "2020-01-10")
        s, e = clamp_date_range("2019-01-01", "2020-06-01")
        self.assertEqual(e, "2020-01-10")
        self.assertLessEqual(s, e)


if __name__ == "__main__":
    unittest.main()
