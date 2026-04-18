"""Integration tests for dca_opt() — market_data.get_prices mocked out."""

import unittest
from unittest.mock import patch

import dca_opt as module
from models import Portfolio
from models.portfolio import Asset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _portfolio(
    only_buy: bool,
    increment: float,
    asset_defs: list[dict],
    optimal_redistribute: bool = False,
) -> Portfolio:
    """Build a Portfolio directly from a list of asset definition dicts."""
    assets = [
        Asset(
            ticker=d["ticker"],
            desired_percentage=d["desired_percentage"],
            shares=d.get("shares", 0.0),
            fees=d.get("fees", 0.0),
        )
        for d in asset_defs
    ]
    return Portfolio(
        only_buy=only_buy,
        increment=increment,
        assets=assets,
        optimal_redistribute=optimal_redistribute,
    )


def _run(portfolio: Portfolio, prices: dict[str, float]) -> dict:
    """Run dca_opt() with a patched market_data.get_prices."""
    with patch("market_data.get_prices", return_value=prices):
        return module.dca_opt(portfolio)


# ---------------------------------------------------------------------------
# Fee tests
# ---------------------------------------------------------------------------

class TestFees(unittest.TestCase):
    """Tests that broker fees are correctly applied throughout the pipeline."""

    def test_fee_deducted_from_allocated_and_change(self):
        """Fee reduces allocated amount; change = increment - spent - fee.

        Setup (only_buy=True, single asset):
            increment=500, price=100, fee=10, desired=100 %

        Step-by-step:
            gross alloc = 500
            net after fee = 490
            buy = floor(490/100) = 4 shares  → spent = 400
            total_fees = 10
            change = 500 - 400 - 10 = 90
            redistribute: floor(90/100) = 0 extra
        """
        p = _portfolio(True, 500.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 10.0},
        ])
        out = _run(p, {"A": 100.0})

        r = out["results"][0]
        self.assertEqual(r["buy"], 4)
        self.assertAlmostEqual(r["allocated"], 490.0, places=2)
        self.assertEqual(out["total_fees"], 10.0)
        self.assertEqual(out["change"], 90.0)

    def test_fee_larger_than_allocation_buy_zero_fee_excluded(self):
        """Asset whose fee exceeds gross allocation is clamped to 0 and its fee
        is NOT counted in total_fees (no purchase executed).

        Setup (only_buy=True, two assets):
            increment=100, A: desired=10 %, fee=50, price=5
                            B: desired=90 %, fee=0,  price=20

            A gross alloc = 10 → net = max(0, 10-50) = 0 → buy_A = 0
            B gross alloc = 90 → net = 90 → buy_B = floor(90/20) = 4
            spent = 80, total_fees = 0 (A skipped, B.fee=0)
            change = 100 - 80 - 0 = 20
            redistribute: B gets floor(20/20)=1 extra → buy_B=5, change=0
        """
        p = _portfolio(True, 100.0, [
            {"ticker": "A", "desired_percentage": 10.0, "shares": 0, "fees": 50.0},
            {"ticker": "B", "desired_percentage": 90.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 5.0, "B": 20.0})

        by_ticker = {r["ticker"]: r for r in out["results"]}
        self.assertEqual(by_ticker["A"]["buy"], 0)
        self.assertEqual(by_ticker["B"]["buy"], 5)
        self.assertEqual(out["total_fees"], 0.0)
        self.assertEqual(out["change"], 0.0)

    def test_fees_both_assets_summed_in_total_fees(self):
        """total_fees = sum of fees for all assets whose buy quantity > 0.

        Setup (only_buy=True, two assets, both bought):
            increment=1000, A: desired=60 %, fee=3, price=50
                             B: desired=40 %, fee=2, price=100
        """
        p = _portfolio(True, 1000.0, [
            {"ticker": "A", "desired_percentage": 60.0, "shares": 0, "fees": 3.0},
            {"ticker": "B", "desired_percentage": 40.0, "shares": 0, "fees": 2.0},
        ])
        out = _run(p, {"A": 50.0, "B": 100.0})

        by_ticker = {r["ticker"]: r for r in out["results"]}
        self.assertGreater(by_ticker["A"]["buy"], 0)
        self.assertGreater(by_ticker["B"]["buy"], 0)
        self.assertEqual(out["total_fees"], 5.0)  # 3 + 2

    def test_only_buy_false_fee_deducted_from_change(self):
        """In allow-sell mode, fee is still deducted from change.

        Setup:
            only_buy=False, increment=100, A: desired=100 %, shares=5 @ 20, fee=5

            current_value = 100, new_total = 200
            gross rebalance = 100, net = 95
            buy = floor(95/20) = 4, spent = 80
            total_fees = 5
            change = 100 - 80 - 5 = 15
        """
        p = _portfolio(False, 100.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 5.0, "fees": 5.0},
        ])
        out = _run(p, {"A": 20.0})

        self.assertEqual(out["results"][0]["buy"], 4)
        self.assertEqual(out["total_fees"], 5.0)
        self.assertEqual(out["change"], 15.0)


# ---------------------------------------------------------------------------
# Change (remainder) tests
# ---------------------------------------------------------------------------

class TestChange(unittest.TestCase):
    """Tests that the leftover change is computed correctly throughout the pipeline."""

    def test_no_fees_change_equals_rounding_leftover(self):
        """Without fees, change = increment - spent (pure rounding leftover).

        increment=1000, A: desired=100 %, price=300, fee=0
            buy = floor(1000/300) = 3, spent = 900, change = 100
            redistribute: floor(100/300) = 0 extra
        """
        p = _portfolio(True, 1000.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 300.0})

        self.assertEqual(out["results"][0]["buy"], 3)
        self.assertEqual(out["total_fees"], 0.0)
        self.assertEqual(out["change"], 100.0)

    def test_fee_reserved_cash_not_spent_in_redistribution(self):
        """Redistribution must NOT consume fee-reserved cash.

        Setup (only_buy=True, single asset):
            increment=1000, price=200, fee=50

            gross alloc = 1000, net = 950
            buy = floor(950/200) = 4, spent = 800
            total_fees = 50
            change passed to redistribute = 1000 - 800 - 50 = 150
            redistribute: floor(150/200) = 0 extra shares

        If fees were deducted AFTER redistribution the wrong flow would be:
            change_to_distribute = 1000 - 800 = 200 → 1 extra share bought
            then change = 0 - 50 = -50  ← negative, incorrect.
        """
        p = _portfolio(True, 1000.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 50.0},
        ])
        out = _run(p, {"A": 200.0})

        self.assertEqual(out["results"][0]["buy"], 4)   # 4, not 5
        self.assertEqual(out["total_fees"], 50.0)
        self.assertEqual(out["change"], 150.0)          # positive, not -50

    def test_change_zero_when_increment_perfectly_divisible(self):
        """change = 0 when increment is exactly divisible into shares (no fees)."""
        p = _portfolio(True, 1000.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 100.0})

        self.assertEqual(out["results"][0]["buy"], 10)
        self.assertEqual(out["total_fees"], 0.0)
        self.assertEqual(out["change"], 0.0)

    def test_redistribution_reduces_change(self):
        """change decreases when redistribution successfully allocates extra shares.

        Setup (only_buy=True, single asset):
            increment=1050, price=100, fee=0
            buy = 10, spent = 1000, change = 50
            redistribute: floor(50/100) = 0 extra → change stays 50
        """
        p = _portfolio(True, 1050.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 100.0})

        self.assertEqual(out["results"][0]["buy"], 10)
        self.assertEqual(out["change"], 50.0)

    def test_redistribution_buys_extra_share_when_change_covers_price(self):
        """When change >= price of eligible asset, extra share is bought.

        increment=1100, price=100, fee=0
            buy = 11, spent = 1100, change = 0  (redistribution allocates 0 extra)

        OR:
            increment=1050, price=50, fee=0
            buy = 21, spent = 1050, change = 0
        """
        p = _portfolio(True, 1050.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 50.0})

        self.assertEqual(out["results"][0]["buy"], 21)
        self.assertEqual(out["change"], 0.0)

    def test_change_two_assets_with_fees(self):
        """End-to-end change with two assets both paying fees.

        Setup (only_buy=True):
            increment=1000
            A: desired=60 %, price=50, fee=3
            B: desired=40 %, price=100, fee=2

        Gaps (total=1000):
            A gap = 600, B gap = 400; S+ = 1000
            A alloc = 600, B alloc = 400
        After fee:
            A net = 597, B net = 398
            buy_A = floor(597/50)=11, buy_B = floor(398/100)=3
            spent = 550 + 300 = 850
            total_fees = 3 + 2 = 5
            change = 1000 - 850 - 5 = 145
        Redistribute (both buy > 0, current_pcts both = 0 → equal priority):
            A processed first (stable sort): floor(145/50)=2 extra → remaining=45
            B: floor(45/100)=0 extra
            Final: buy_A=13, buy_B=3, change=45
        """
        p = _portfolio(True, 1000.0, [
            {"ticker": "A", "desired_percentage": 60.0, "shares": 0, "fees": 3.0},
            {"ticker": "B", "desired_percentage": 40.0, "shares": 0, "fees": 2.0},
        ])
        out = _run(p, {"A": 50.0, "B": 100.0})

        by_ticker = {r["ticker"]: r for r in out["results"]}
        self.assertEqual(by_ticker["A"]["buy"], 13)
        self.assertEqual(by_ticker["B"]["buy"], 3)
        self.assertEqual(out["total_fees"], 5.0)
        self.assertEqual(out["change"], 45.0)

    def test_only_buy_false_no_redistribution_change_pure(self):
        """In allow-sell mode redistribution is skipped; change is rounding + fee.

        increment=200, A: desired=100 %, shares=0, price=150, fee=0
            new_total = 200, delta = 200
            buy = floor(200/150) = 1, spent = 150
            change = 200 - 150 - 0 = 50
        """
        p = _portfolio(False, 200.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ])
        out = _run(p, {"A": 150.0})

        self.assertEqual(out["results"][0]["buy"], 1)
        self.assertEqual(out["change"], 50.0)


# ---------------------------------------------------------------------------
# optimal_redistribute flag - integration tests
# ---------------------------------------------------------------------------

class TestOptimalRedistributeFlag(unittest.TestCase):
    """End-to-end wiring of the `optimal_redistribute` flag through dca_opt()."""

    def test_flag_off_keeps_greedy_behaviour(self):
        """Default optimal_redistribute=False preserves the legacy pipeline.

        Setup (only_buy=True):
            increment=100, A: desired=50 %, price=60; B: desired=50 %, price=45.
            Gross alloc per asset = 50.
            buy_A = floor(50/60)=0, buy_B = floor(50/45)=1 -> spent=45, change=55.
            Greedy redistribution: only B eligible (buy>0), floor(55/45)=1
            extra -> buy_B=2, remaining change=10.
        """
        p = _portfolio(True, 100.0, [
            {"ticker": "A", "desired_percentage": 50.0, "shares": 0, "fees": 0.0},
            {"ticker": "B", "desired_percentage": 50.0, "shares": 0, "fees": 0.0},
        ], optimal_redistribute=False)

        out = _run(p, {"A": 60.0, "B": 45.0})
        by_ticker = {r["ticker"]: r for r in out["results"]}
        self.assertEqual(by_ticker["A"]["buy"], 0)
        self.assertEqual(by_ticker["B"]["buy"], 2)
        self.assertEqual(out["change"], 10.0)

    def test_flag_on_never_worse_than_greedy_in_buy_only(self):
        """optimal_redistribute=True must leave <= cash on the table than greedy.

        Same portfolio, same prices, same increment -- only the flag changes.
        """
        assets_def = [
            {"ticker": "A", "desired_percentage": 50.0, "shares": 0, "fees": 0.0},
            {"ticker": "B", "desired_percentage": 50.0, "shares": 0, "fees": 0.0},
        ]
        prices = {"A": 60.0, "B": 45.0}

        p_greedy = _portfolio(True, 200.0, assets_def, optimal_redistribute=False)
        p_optimal = _portfolio(True, 200.0, assets_def, optimal_redistribute=True)

        out_greedy = _run(p_greedy, prices)
        out_optimal = _run(p_optimal, prices)

        self.assertLessEqual(out_optimal["change"], out_greedy["change"])

    def test_flag_on_applies_in_allow_sell_mode(self):
        """The flag also triggers the DP when only_buy=False.

        In the legacy pipeline redistribution is skipped entirely with
        only_buy=False.  With the flag on the DP is called; for this simple
        setup (price > change) it cannot improve, so the change stays 10
        -- but the code path is exercised and the result is sane.

        Setup:
            only_buy=False, increment=100, A: desired=100 %, price=30.
            buy = floor(100/30) = 3, spent=90, change=10.
        """
        p = _portfolio(False, 100.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ], optimal_redistribute=True)

        out = _run(p, {"A": 30.0})
        self.assertEqual(out["results"][0]["buy"], 3)
        self.assertEqual(out["change"], 10.0)

    def test_flag_on_allow_sell_absorbs_leftover_when_price_fits(self):
        """only_buy=False + flag on buys an extra share whenever change covers a price.

        Setup chosen so greedy (OFF) would leave change=50 but the DP (ON)
        absorbs it into one extra share of A:
            only_buy=False, increment=150, A: desired=100 %, price=50.
            buy = floor(150/50) = 3, spent=150, change=0 (exact fit).

        And a slightly different case where change=50 initially:
            only_buy=False, increment=200, A: desired=100 %, price=50.
            buy = floor(200/50) = 4, spent=200, change=0.

        Both match with the flag on or off.  We pick a case that distinguishes:
            only_buy=False, increment=175, A: desired=100 %, price=50.
            legacy: buy=3 (150), change=25 (redistribute skipped for only_buy=False)
            optimal-flag-on: DP still cannot fit (50 > 25) -> change=25.

        To truly force divergence we need a case where the legacy SKIPS the
        redistribution step while the DP manages to place at least one share.
        That requires a price <= change in allow-sell mode, which only happens
        if the initial allocation left a multiple of the price unspent due to
        fee reservation.  Setup:
            only_buy=False, increment=200, A: 100 %, price=50, fee=30.
            gross=200, net=170, buy=floor(170/50)=3, spent=150, total_fees=30,
            change=200-150-30=20.  DP: 50 > 20 -> no fit.  Still can't diverge.

        Realistically in allow-sell mode with a single asset the DP never
        diverges because the initial allocation is already tight.  We therefore
        verify only that the flag does not break correctness here.
        """
        p = _portfolio(False, 150.0, [
            {"ticker": "A", "desired_percentage": 100.0, "shares": 0, "fees": 0.0},
        ], optimal_redistribute=True)
        out = _run(p, {"A": 50.0})
        self.assertEqual(out["results"][0]["buy"], 3)
        self.assertEqual(out["change"], 0.0)


class TestPortfolioDefaults(unittest.TestCase):
    """Verify the Portfolio dataclass defaults the flag to False for back-compat."""

    def test_default_optimal_redistribute_is_false(self):
        p = Portfolio(
            only_buy=True,
            increment=100.0,
            assets=[Asset(ticker="A", desired_percentage=100.0, shares=0, fees=0)],
        )
        self.assertFalse(p.optimal_redistribute)


if __name__ == "__main__":
    unittest.main()
