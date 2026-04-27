import unittest

from tradingagents.graph.finalize_decision import finalize_decision_passthrough_node
from tradingagents.graph.synthetic_investment_plan import build_synthetic_investment_plan


class TestSyntheticInvestmentPlan(unittest.TestCase):
    def test_empty_reports_produces_disclosure_only(self) -> None:
        text = build_synthetic_investment_plan({})
        self.assertIn("Synthesized investment plan", text)
        self.assertNotIn("## ", text)

    def test_a1_market_only(self) -> None:
        text = build_synthetic_investment_plan(
            {
                "market_report": "market text",
                "sentiment_report": "",
                "news_report": "",
                "fundamentals_report": "",
            }
        )
        self.assertIn("## Market Analyst", text)
        self.assertIn("market text", text)
        self.assertNotIn("## Social Media Analyst", text)

    def test_a2_all_reports(self) -> None:
        text = build_synthetic_investment_plan(
            {
                "market_report": "m",
                "sentiment_report": "s",
                "news_report": "n",
                "fundamentals_report": "f",
            }
        )
        self.assertIn("## Market Analyst", text)
        self.assertIn("## Social Media Analyst", text)
        self.assertIn("## News Analyst", text)
        self.assertIn("## Fundamentals Analyst", text)


class TestFinalizeDecision(unittest.TestCase):
    def test_passthrough(self) -> None:
        out = finalize_decision_passthrough_node({"trader_investment_plan": "FINAL ..."})
        self.assertEqual(out["final_trade_decision"], "FINAL ...")


if __name__ == "__main__":
    unittest.main()

