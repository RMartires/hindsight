import os
import unittest

from tradingagents.paper_ablation import (
    PAPER_ABLATION_LABELS,
    apply_paper_ablation_to_config,
)


class TestPaperAblation(unittest.TestCase):
    def tearDown(self) -> None:
        for key in (
            "PAPER_ABLATION",
        ):
            os.environ.pop(key, None)

    def test_labels_frozen(self) -> None:
        self.assertEqual(PAPER_ABLATION_LABELS, frozenset({"a1", "a2", "a3", "full"}))

    def test_a1(self) -> None:
        os.environ["PAPER_ABLATION"] = "a1"
        cfg: dict = {"paper_ablation": "full"}
        apply_paper_ablation_to_config(cfg)
        self.assertEqual(cfg["selected_analysts"], ["market"])
        self.assertFalse(cfg["run_investment_debate"])
        self.assertFalse(cfg["run_risk_phase"])
        self.assertEqual(cfg["paper_ablation"], "a1")

    def test_a2(self) -> None:
        os.environ["PAPER_ABLATION"] = "a2"
        cfg: dict = {"paper_ablation": "full"}
        apply_paper_ablation_to_config(cfg)
        self.assertEqual(
            cfg["selected_analysts"],
            ["market", "social", "news", "fundamentals"],
        )
        self.assertFalse(cfg["run_investment_debate"])
        self.assertFalse(cfg["run_risk_phase"])

    def test_a3(self) -> None:
        os.environ["PAPER_ABLATION"] = "a3"
        cfg: dict = {"paper_ablation": "full"}
        apply_paper_ablation_to_config(cfg)
        self.assertTrue(cfg["run_investment_debate"])
        self.assertFalse(cfg["run_risk_phase"])

    def test_full(self) -> None:
        os.environ["PAPER_ABLATION"] = "full"
        cfg: dict = {"paper_ablation": "a1"}
        apply_paper_ablation_to_config(cfg)
        self.assertTrue(cfg["run_investment_debate"])
        self.assertTrue(cfg["run_risk_phase"])

    def test_env_case_insensitive(self) -> None:
        os.environ["PAPER_ABLATION"] = "A1"
        cfg: dict = {"paper_ablation": "full"}
        apply_paper_ablation_to_config(cfg)
        self.assertEqual(cfg["paper_ablation"], "a1")
        self.assertEqual(cfg["selected_analysts"], ["market"])

    def test_unset_uses_config_fallback_then_full(self) -> None:
        # No env: use cfg's paper_ablation
        cfg: dict = {"paper_ablation": "a2"}
        apply_paper_ablation_to_config(cfg)
        self.assertEqual(cfg["paper_ablation"], "a2")

    def test_unknown_raises(self) -> None:
        os.environ["PAPER_ABLATION"] = "nope"
        cfg: dict = {"paper_ablation": "full"}
        with self.assertRaises(ValueError) as ctx:
            apply_paper_ablation_to_config(cfg)
        self.assertIn("nope", str(ctx.exception))
        self.assertIn("a1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
