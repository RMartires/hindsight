import unittest

from tradingagents.backtest.zerodha_fees import (
    fees_for_leg_inr,
    zerodha_fees_buy_delivery_inr,
    zerodha_fees_sell_delivery_inr,
)


class TestZerodhaFees(unittest.TestCase):
    def test_delivery_buy_positive(self) -> None:
        f = zerodha_fees_buy_delivery_inr(100_000.0)
        self.assertGreater(f, 0.0)

    def test_delivery_sell_includes_dp(self) -> None:
        f = zerodha_fees_sell_delivery_inr(100_000.0)
        self.assertGreater(f, 15.0)

    def test_fees_for_leg_flat_zero_when_unknown_model(self) -> None:
        self.assertEqual(
            fees_for_leg_inr(cost_model="flat_bps", side="BUY", notional_inr=10_000.0),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
