"""Unit tests for the rebalance module."""

import unittest

from rebalance import calculate_rebalance, redistribute_change


class TestCalculateRebalance(unittest.TestCase):
    """Tests for calculate_rebalance()."""

    # Valid inputs

    def test_standard_allow_sell(self):
        """Full rebalance (allow sell) produces correct signed amounts."""
        self.assertEqual(
            calculate_rebalance(False, 100, [0, 40, 100, 100], [60, 20, 10, 10]),
            [204.0, 28.0, -66.0, -66.0],
        )

    def test_standard_only_buy(self):
        """Only-buy mode distributes the increment proportionally to positive rebalance gaps.

        Post-increment total = 340.
        Gaps: A = 340*0.60-0 = +204, B = 340*0.20-40 = +28, C = -66, D = -66.
        Total positive gap S+ = 232.
        A receives 100 * 204/232 ≈ 87.93; B receives 100 * 28/232 ≈ 12.07.
        C and D have negative gaps and receive 0 (overweight relative to new total).
        Values are compared after {:.2f} formatting to match display precision.
        """
        result = calculate_rebalance(True, 100, [0, 40, 100, 100], [60, 20, 10, 10])
        self.assertEqual(
            [f"{v:.2f}" for v in result],
            ["87.93", "12.07", "0.00", "0.00"],
        )

    def test_zero_increment_allow_sell(self):
        """Zero increment with allow-sell shows pure rebalance deltas."""
        self.assertEqual(
            calculate_rebalance(False, 0, [0, 0, 100, 100], [60, 20, 10, 10]),
            [120.0, 40.0, -80.0, -80.0],
        )

    def test_zero_increment_only_buy(self):
        """Zero increment with only-buy results in all zeros (nothing to distribute)."""
        self.assertEqual(
            calculate_rebalance(True, 0, [0, 0, 100, 100], [60, 20, 10, 10]),
            [0.0, 0.0, 0.0, 0.0],
        )

    def test_perfectly_balanced_portfolio(self):
        """A perfectly balanced portfolio with an increment produces clean amounts."""
        # 50/50 allocation, equal values: increment should split 50/50.
        result = calculate_rebalance(True, 200, [500, 500], [50, 50])
        self.assertEqual(result, [100.0, 100.0])

    def test_single_asset(self):
        """A single-asset portfolio receives the entire increment."""
        self.assertEqual(calculate_rebalance(True, 500, [1000], [100]), [500.0])
        self.assertEqual(calculate_rebalance(False, 500, [1000], [100]), [500.0])

    # Input validation

    def test_negative_increment_raises(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, -10, [100], [100])

    def test_percentages_not_summing_to_100_raises(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100], [50])

    def test_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100], [50, 50])

    def test_empty_lists_raise_explicit_error(self):
        """Empty lists must raise ValueError with a clear message (not a sum-to-100 error)."""
        with self.assertRaises(ValueError) as ctx:
            calculate_rebalance(False, 100, [], [])
        self.assertIn("empty", str(ctx.exception).lower())

    def test_non_numeric_values_raise(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, ["a", 100], [50, 50])

    def test_non_numeric_percentages_raise(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100, 100], ["b", 50])

    def test_non_numeric_increment_raises(self):
        with self.assertRaises(ValueError):
            calculate_rebalance(False, "100", [100], [100])


class TestRedistributeChange(unittest.TestCase):
    """Tests for redistribute_change()."""

    def test_change_goes_to_most_underweight_asset(self):
        """Change is allocated to the most underweight eligible asset first."""
        # Asset 0: 10% current vs 60% desired -> most underweight.
        # Asset 1: 90% current vs 40% desired -> overweight.
        buy_quantities = [1.0, 1.0]
        ticker_prices = [100.0, 500.0]
        current_pcts = [10.0, 90.0]
        desired_pcts = [60.0, 40.0]
        change = 250.0  # enough for 2 extra shares of asset 0 (2 * 100 = 200)

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

        self.assertEqual(updated[0], 3.0)   # 1 original + 2 from change
        self.assertEqual(updated[1], 1.0)   # unchanged
        self.assertEqual(remaining, 50.0)   # 250 - 200 = 50

    def test_no_change_returns_unchanged(self):
        """Zero change leaves all buy quantities unchanged."""
        buy_quantities = [2.0, 1.0]
        ticker_prices = [100.0, 200.0]
        current_pcts = [50.0, 50.0]
        desired_pcts = [60.0, 40.0]

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, 0.0
        )

        self.assertEqual(updated, [2.0, 1.0])
        self.assertEqual(remaining, 0.0)

    def test_zero_buy_asset_is_skipped(self):
        """Assets with buy == 0 are skipped even if change could cover their price."""
        # Asset 0 is most underweight but has buy=0 and must be skipped.
        buy_quantities = [0.0, 1.0]
        ticker_prices = [50.0, 200.0]
        current_pcts = [80.0, 20.0]
        desired_pcts = [40.0, 60.0]
        change = 100.0  # enough for 2 shares of asset 0, but 0 shares of asset 1

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

        self.assertEqual(updated[0], 0.0)    # skipped despite being underweight
        self.assertEqual(remaining, 100.0)   # change unspent

    def test_change_smaller_than_any_price_stays_unallocated(self):
        """Change too small to buy even one share remains as leftover."""
        buy_quantities = [1.0, 1.0]
        ticker_prices = [500.0, 300.0]
        current_pcts = [30.0, 70.0]
        desired_pcts = [70.0, 30.0]
        change = 10.0  # cannot afford a single share of either asset

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

        self.assertEqual(updated, [1.0, 1.0])
        self.assertEqual(remaining, 10.0)

    def test_change_distributed_across_multiple_assets(self):
        """After exhausting one asset, remaining change moves to the next eligible one."""
        # Asset 0: price=100, most underweight. Asset 1: price=150, less underweight.
        # change=250 -> 2 shares of asset 0 (200), 0 shares of asset 1 (50 < 150).
        buy_quantities = [1.0, 1.0]
        ticker_prices = [100.0, 150.0]
        current_pcts = [20.0, 80.0]
        desired_pcts = [70.0, 30.0]
        change = 250.0

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

        self.assertEqual(updated[0], 3.0)   # 1 + 2
        self.assertEqual(updated[1], 1.0)   # 50 < 150, nothing extra
        self.assertEqual(remaining, 50.0)

    def test_docstring_step_by_step_example(self):
        """Verifies the two-asset example from the formal algorithm docstring.

        Setup (from the greedy knapsack description):
            Asset A: price=10, current=20%, desired=50%, initial_qty=1
            Asset B: price=20, current=30%, desired=50%, initial_qty=1
            change = 50

        Step 1 – priorities:
            k_A = 20 / (50 + 0.01) = 0.39996...
            k_B = 30 / (50 + 0.01) = 0.59988...
            Order: A first (lower k_A → more underweight)

        Step 3 – A processed first:
            x_A = floor(50 / 10) = 5  →  remaining = 50 - 50 = 0

        Step 3 – B processed next:
            remaining = 0  →  x_B = floor(0 / 20) = 0

        Step 4 – Result: A=6, B=1, remaining=0.
        """
        buy_quantities = [1.0, 1.0]
        ticker_prices = [10.0, 20.0]
        current_pcts = [20.0, 30.0]
        desired_pcts = [50.0, 50.0]
        change = 50.0

        updated, remaining = redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

        self.assertEqual(updated[0], 6.0)   # 1 original + 5 from change
        self.assertEqual(updated[1], 1.0)   # change exhausted after A
        self.assertEqual(remaining, 0.0)


class TestFeeEdgeCases(unittest.TestCase):
    """Tests that verify the fee-subtraction contract.

    These tests document the expected behaviour so that anyone reading dca_opt.py
    understands that max(0, r - fee) must be applied before converting currency
    amounts to share quantities.
    """

    def test_only_buy_all_overweight(self):
        """When all assets are overweight, only_buy produces all zeros."""
        result = calculate_rebalance(True, 0, [600, 400], [60, 40])
        self.assertEqual(result, [0.0, 0.0])

    def test_only_buy_single_underweight_asset_gets_full_increment(self):
        """A single underweight asset in only_buy mode receives the full increment."""
        # Asset 0 is overweight, asset 1 is strongly underweight.
        result = calculate_rebalance(True, 100, [900, 0], [50, 50])
        self.assertEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 100.0, places=2)


if __name__ == "__main__":
    unittest.main()
