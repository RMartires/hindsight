import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.local_db.indicator import get_indicators
from tradingagents.dataflows.local_db.prefetch_check import verify_local_ohlcv_coverage
from tradingagents.dataflows.local_db.stock import format_ohlcv_block, get_stock_data
from tradingagents.dataflows.local_db.store import (
    LocalDataError,
    MarketDataStore,
    chunk_date_ranges,
    normalize_symbol_key,
)


def _sample_ohlcv_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Date": datetime(2024, 1, 1),
                "Open": 2400.0,
                "High": 2450.0,
                "Low": 2390.0,
                "Close": 2440.0,
                "Adj Close": 2440.0,
                "Volume": 10,
            },
            {
                "Date": datetime(2024, 1, 2),
                "Open": 2440.0,
                "High": 2500.0,
                "Low": 2430.0,
                "Close": 2480.0,
                "Adj Close": 2480.0,
                "Volume": 20,
            },
        ]
    )


class TestLocalDbStore(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = f"{self._tmpdir.name}/test.duckdb"
        set_config({"market_db_path": self.db_path})

    def tearDown(self):
        self._tmpdir.cleanup()
        set_config({"market_db_path": None})

    def test_normalize_symbol_key(self):
        self.assertEqual(normalize_symbol_key(" reliance.ns "), "RELIANCE.NS")

    def test_upsert_and_load(self):
        store = MarketDataStore(db_path=self.db_path)
        try:
            n = store.upsert_ohlcv_df("RELIANCE.NS", _sample_ohlcv_df())
            self.assertEqual(n, 2)
            df = store.load_ohlcv_df("RELIANCE.NS", "2024-01-01", "2024-01-31")
            self.assertEqual(len(df), 2)
            present = store.dates_present("RELIANCE.NS", ["2024-01-01", "2024-01-02", "2024-01-03"])
            self.assertEqual(present, {"2024-01-01", "2024-01-02"})
        finally:
            store.close()

    def test_get_stock_data_format(self):
        store = MarketDataStore(db_path=self.db_path)
        try:
            store.upsert_ohlcv_df("RELIANCE.NS", _sample_ohlcv_df())
        finally:
            store.close()

        out = get_stock_data("RELIANCE.NS", "2024-01-01", "2024-01-31")
        self.assertIn("# Stock data for RELIANCE.NS from 2024-01-01 to 2024-01-31", out)
        self.assertIn("Date,Open,High,Low,Close,Adj Close,Volume", out)
        self.assertIn("2024-01-01,2400.0,2450.0,2390.0,2440.0,2440.0", out)

    def test_get_stock_data_missing_raises(self):
        with self.assertRaises(LocalDataError):
            get_stock_data("MISSING.NS", "2024-01-01", "2024-01-31")

    def test_prefetch_check_missing(self):
        with self.assertRaises(LocalDataError):
            verify_local_ohlcv_coverage("RELIANCE.NS", ["2024-01-02"], db_path=self.db_path)

    def test_prefetch_check_ok(self):
        store = MarketDataStore(db_path=self.db_path)
        try:
            store.upsert_ohlcv_df("RELIANCE.NS", _sample_ohlcv_df())
        finally:
            store.close()
        verify_local_ohlcv_coverage("RELIANCE.NS", ["2024-01-02"], db_path=self.db_path)

    def test_chunk_date_ranges(self):
        chunks = chunk_date_ranges("2020-01-01", "2025-12-31", max_days=2000)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0][0], "2020-01-01")


class TestLocalIndicators(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = f"{self._tmpdir.name}/test.duckdb"
        set_config({"market_db_path": self.db_path})
        store = MarketDataStore(db_path=self.db_path)
        # Seed enough history for RSI (need multiple rows)
        rows = []
        for i in range(30):
            d = datetime(2024, 1, 1)
            from datetime import timedelta

            dt = d + timedelta(days=i)
            close = 100.0 + i
            rows.append(
                {
                    "Date": dt,
                    "Open": close,
                    "High": close + 1,
                    "Low": close - 1,
                    "Close": close,
                    "Adj Close": close,
                    "Volume": 100,
                }
            )
        store.upsert_ohlcv_df("RELIANCE.NS", pd.DataFrame(rows))
        store.close()

    def tearDown(self):
        self._tmpdir.cleanup()
        set_config({"market_db_path": None})

    @patch("tradingagents.dataflows.local_db.indicator.indicator_bulk_date_range")
    def test_get_indicators_window(self, mock_range):
        mock_range.return_value = ("2024-01-01", "2024-01-30")
        out = get_indicators("RELIANCE.NS", "rsi", "2024-01-30", look_back_days=1)
        self.assertIn("## rsi values from 2024-01-29 to 2024-01-30:", out)
        self.assertIn("2024-01-30:", out)


class TestPrefetchChunks(unittest.TestCase):
    @patch("tradingagents.dataflows.kite_ohlcv.fetch_kite_ohlcv_df")
    def test_prefetch_upserts(self, mock_fetch):
        mock_fetch.return_value = _sample_ohlcv_df()
        with tempfile.TemporaryDirectory() as tmp:
            db_path = f"{tmp}/market.duckdb"
            set_config({"market_db_path": db_path})
            store = MarketDataStore(db_path=db_path)
            try:
                df = mock_fetch("RELIANCE.NS", "2024-01-01", "2024-01-02")
                n = store.upsert_ohlcv_df("RELIANCE.NS", df)
                self.assertEqual(n, 2)
                self.assertEqual(store.count_rows("RELIANCE.NS", "2024-01-01", "2024-01-02"), 2)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
