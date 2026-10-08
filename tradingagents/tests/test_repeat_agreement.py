"""Modal agreement on repeated decisions. No model calls."""

import unittest

from tradingagents.backtest.repeat_agreement import modal_agreement, wilson_interval


class TestModalAgreement(unittest.TestCase):
    def test_eight_of_ten_passes_the_point_estimate_only(self) -> None:
        score = modal_agreement(["BUY"] * 8 + ["HOLD"] * 2)
        self.assertEqual(score.mode, "BUY")
        self.assertAlmostEqual(score.modal_share, 0.8)
        self.assertTrue(score.passes_bar)
        self.assertFalse(score.proven_bar)
        self.assertLess(score.wilson_low, 0.80)

    def test_unanimous_twenty_clears_the_wilson_bound(self) -> None:
        score = modal_agreement(["SELL"] * 20)
        self.assertTrue(score.passes_bar)
        self.assertTrue(score.proven_bar)
        self.assertGreaterEqual(score.wilson_low, 0.80)

    def test_tie_fails(self) -> None:
        score = modal_agreement(["BUY", "HOLD"] * 5)
        self.assertIsNone(score.mode)
        self.assertEqual(score.modal_share, 0.0)
        self.assertFalse(score.passes_bar)
        self.assertFalse(score.proven_bar)

    def test_case_is_folded(self) -> None:
        score = modal_agreement(["buy", " Buy ", "BUY"])
        self.assertEqual(score.mode, "BUY")
        self.assertEqual(score.counts, {"BUY": 3})

    def test_blank_and_empty_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            modal_agreement([])
        with self.assertRaises(ValueError):
            modal_agreement(["BUY", "  "])

    def test_wilson_covers_a_known_proportion(self) -> None:
        low, high = wilson_interval(8, 10)
        self.assertLess(low, 0.8)
        self.assertGreater(high, 0.8)
