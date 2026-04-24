import unittest

import pandas as pd


class TestIndicatorLibrary(unittest.TestCase):
    def _sample_ohlcv(self) -> pd.DataFrame:
        # Small deterministic OHLCV dataset with monotonic-ish prices and non-zero volume.
        rows = [
            {"Date": "2024-01-01", "Open": 100, "High": 105, "Low": 99, "Close": 104, "Volume": 1000},
            {"Date": "2024-01-02", "Open": 104, "High": 106, "Low": 101, "Close": 102, "Volume": 1200},
            {"Date": "2024-01-03", "Open": 102, "High": 107, "Low": 101, "Close": 106, "Volume": 900},
            {"Date": "2024-01-04", "Open": 106, "High": 110, "Low": 105, "Close": 109, "Volume": 1500},
            {"Date": "2024-01-05", "Open": 109, "High": 112, "Low": 108, "Close": 111, "Volume": 1300},
        ]
        return pd.DataFrame.from_records(rows)

    def test_compute_indicators_tier1_subset(self):
        from tradingagents.dataflows.indicator_library import compute_indicators

        df = compute_indicators(self._sample_ohlcv(), ["rsi", "macd", "atr"])
        self.assertIn("rsi", df.columns)
        self.assertIn("macd", df.columns)
        self.assertIn("atr", df.columns)
        self.assertTrue(len(df.index) > 0)

    def test_compute_indicators_unknown_raises(self):
        from tradingagents.dataflows.indicator_library import compute_indicators

        with self.assertRaises(ValueError):
            compute_indicators(self._sample_ohlcv(), ["not_a_real_indicator"])


if __name__ == "__main__":
    unittest.main()

