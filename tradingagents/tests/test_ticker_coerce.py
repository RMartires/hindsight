"""Tests for anonymized ticker coercion before vendor calls."""

import unittest

from tradingagents.anonymization.ticker_map import coerce_agent_symbol


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


if __name__ == "__main__":
    unittest.main()
