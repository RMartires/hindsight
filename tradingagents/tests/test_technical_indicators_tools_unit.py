"""Unit tests for LangChain technical indicator tool wrapper."""

from unittest.mock import patch

import unittest

from tradingagents.dataflows import config as config_mod


class TestTechnicalIndicatorTool(unittest.TestCase):
    def tearDown(self) -> None:
        config_mod.initialize_config()

    @patch("tradingagents.agents.utils.technical_indicators_tools.route_to_vendor")
    def test_omit_curr_date_uses_active_trade_date(self, mock_route):
        from tradingagents.agents.utils.technical_indicators_tools import get_indicators

        config_mod.set_config({"active_trade_date": "2024-06-03"})
        mock_route.return_value = "indicator-body"
        out = get_indicators.invoke({"symbol": "RELIANCE", "indicator": "rsi", "curr_date": None})
        self.assertEqual(out, "indicator-body")
        mock_route.assert_called_once_with(
            "get_indicators",
            "RELIANCE",
            "rsi",
            "2024-06-03",
            30,
        )

    @patch("tradingagents.agents.utils.technical_indicators_tools.route_to_vendor")
    def test_indicator_alias_normalized_before_vendor(self, mock_route):
        from tradingagents.agents.utils.technical_indicators_tools import get_indicators

        config_mod.set_config({"active_trade_date": "2024-06-03"})
        mock_route.return_value = "ok"
        get_indicators.invoke({"symbol": "RELIANCE", "indicator": "50_sma"})
        mock_route.assert_called_once_with(
            "get_indicators",
            "RELIANCE",
            "close_50_sma",
            "2024-06-03",
            30,
        )


if __name__ == "__main__":
    unittest.main()
