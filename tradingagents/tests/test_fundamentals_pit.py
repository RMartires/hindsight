"""Point-in-time filtering for fundamental vendor text."""

import json
import unittest
from unittest.mock import patch

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.fundamentals_pit import apply_fundamentals_point_in_time
from tradingagents.dataflows.interface import VENDOR_METHODS, route_to_vendor

OVERVIEW = """\
# Company Fundamentals for STOCK_0251
# Data retrieved on: 2026-10-03 00:10:16

Name: Tata Consultancy Services Limited
Sector: Technology
Industry: Information Technology Services
Market Cap: 7507531530240
PE Ratio (TTM): 15.08323
52 Week High: 3350.0
50 Day Average: 2275.594
Revenue (TTM): 2758590070784
"""

BALANCE = """\
# Balance Sheet data for STOCK_0251 (annual)
# Data retrieved on: 2026-10-03 00:10:16

,2026-03-31,2025-03-31,2024-03-31,2023-03-31,2022-03-31
Total Assets,1823720000000.0,1596290000000.0,1464490000000.0,1436510000000.0,
Net Income,492100000000.0,485530000000.0,459080000000.0,421470000000.0,400000000000.0
"""

AV_STATEMENTS = json.dumps(
    {
        "symbol": "TCS.NS",
        "annualReports": [
            {"fiscalDateEnding": "2026-03-31", "totalRevenue": "2670210000000"},
            {"fiscalDateEnding": "2024-03-31", "totalRevenue": "2408930000000"},
        ],
        "quarterlyReports": [
            {"fiscalDateEnding": "2025-12-31", "totalRevenue": "1"},
            {"fiscalDateEnding": "2024-03-31", "totalRevenue": "2"},
        ],
    }
)


class TestFundamentalsPointInTime(unittest.TestCase):
    def tearDown(self) -> None:
        set_config({"simulation_data_end": None})

    def test_live_mode_keeps_future_columns(self) -> None:
        set_config({"simulation_data_end": None})
        self.assertEqual(apply_fundamentals_point_in_time(BALANCE), BALANCE)

    def test_statement_drops_columns_after_cutoff(self) -> None:
        set_config({"simulation_data_end": "2024-06-02"})
        out = apply_fundamentals_point_in_time(BALANCE)
        self.assertNotIn("2026-03-31", out)
        self.assertNotIn("2025-03-31", out)
        self.assertNotIn("2026-10-03", out)
        self.assertIn("2024-03-31", out)
        self.assertIn("2023-03-31", out)
        self.assertIn("2022-03-31", out)
        self.assertIn("1464490000000.0", out)
        self.assertNotIn("1823720000000.0", out)
        self.assertIn("Statement periods after 2024-06-02 omitted", out)

    def test_overview_drops_live_snapshot(self) -> None:
        set_config({"simulation_data_end": "2024-06-02"})
        out = apply_fundamentals_point_in_time(OVERVIEW)
        self.assertIn("Tata Consultancy Services Limited", out)
        self.assertIn("Technology", out)
        self.assertIn("Information Technology Services", out)
        self.assertNotIn("Market Cap", out)
        self.assertNotIn("52 Week High", out)
        self.assertNotIn("50 Day Average", out)
        self.assertNotIn("Revenue (TTM)", out)
        self.assertNotIn("2026-10-03", out)
        self.assertIn("Live market snapshot omitted", out)

    def test_alpha_vantage_reports_filtered_by_fiscal_date(self) -> None:
        set_config({"simulation_data_end": "2024-06-02"})
        out = json.loads(apply_fundamentals_point_in_time(AV_STATEMENTS))
        self.assertEqual(
            [row["fiscalDateEnding"] for row in out["annualReports"]],
            ["2024-03-31"],
        )
        self.assertEqual(
            [row["fiscalDateEnding"] for row in out["quarterlyReports"]],
            ["2024-03-31"],
        )

    def test_route_to_vendor_applies_filter(self) -> None:
        set_config({"simulation_data_end": "2024-06-02"})
        with patch.dict(
            VENDOR_METHODS["get_fundamentals"],
            {"yfinance": lambda *args, **kwargs: OVERVIEW},
        ):
            out = route_to_vendor("get_fundamentals", "TCS.NS", "2024-06-03")
        self.assertIn("Tata Consultancy Services Limited", out)
        self.assertNotIn("Market Cap", out)
        self.assertNotIn("2026-10-03", out)


if __name__ == "__main__":
    unittest.main()
