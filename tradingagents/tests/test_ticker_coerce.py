"""Tests for anonymized ticker coercion before vendor calls."""

import unittest

from tradingagents.anonymization.ticker_map import (
    TickerMapper,
    coerce_agent_symbol,
    resolve_ticker_for_vendor,
)


class TestCoerceAgentSymbol(unittest.TestCase):
    def test_no_op_without_anonymization(self):
        self.assertEqual(coerce_agent_symbol("ST", {"enable_anonymization": False}), "ST")

    def test_truncated_st_maps_to_singleton_session_anon(self):
        cfg = {
            "enable_anonymization": True,
            "anonymization_ticker_unmap": {"STOCK_4264": "RELIANCE.NS"},
        }
        self.assertEqual(coerce_agent_symbol("ST", cfg), "STOCK_4264")

    def test_wrong_stock_id_maps_when_single_session_mapper(self):
        cfg = {
            "enable_anonymization": True,
            "anonymization_ticker_unmap": {"STOCK_4264": "RELIANCE.NS"},
        }
        self.assertEqual(coerce_agent_symbol("STOCK_4240", cfg), "STOCK_4264")

    def test_valid_anon_unchanged(self):
        cfg = {
            "enable_anonymization": True,
            "anonymization_ticker_unmap": {"STOCK_4264": "RELIANCE.NS"},
        }
        self.assertEqual(coerce_agent_symbol("STOCK_4264", cfg), "STOCK_4264")

    def test_multi_entry_unmap_no_coercion_for_unknown_stock(self):
        cfg = {
            "enable_anonymization": True,
            "anonymization_ticker_unmap": {
                "STOCK_1111": "AAA.NS",
                "STOCK_2222": "BBB.NS",
            },
        }
        self.assertEqual(coerce_agent_symbol("STOCK_4240", cfg), "STOCK_4240")

    def test_resolve_news_ticker_for_alpha_vantage(self):
        mapper = TickerMapper.for_real_ticker("RELIANCE.NS")
        cfg = {
            "enable_anonymization": True,
            **mapper.to_config_payload(),
            "data_vendors": {"news_data": "alpha_vantage"},
        }
        self.assertEqual(
            resolve_ticker_for_vendor("ST", "get_news", cfg),
            "RELIANCE:NSE",
        )


if __name__ == "__main__":
    unittest.main()
