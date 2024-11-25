"""Unit tests for the rebalance module."""

import unittest
from rebalance import calculate_rebalance


class TestRebalanceFunctions(unittest.TestCase):

    def test_valid_inputs(self):
        # Standard case
        increment = 100
        values = [0, 40, 100, 100]
        percentages = [60, 20, 10, 10]
        self.assertEqual(
            calculate_rebalance(False, increment, values, percentages),
            [204.0, 28.0, -66.0, -66.0]
        )
        self.assertEqual(
            calculate_rebalance(True, increment, values, percentages),
            [87.93, 12.07, 0.0, 0.0]
        )


    def test_zero_increment(self):
        # Case with zero increment
        increment = 0
        values = [0, 0, 100, 100]
        percentages = [60, 20, 10, 10]
        self.assertEqual(
            calculate_rebalance(False, increment, values, percentages),
            [120.0, 40.0, -80.0, -80.0]
        )
        self.assertEqual(
            calculate_rebalance(True, increment, values, percentages),
            [0.0, 0.0, 0.0, 0.0]
        )


    def test_invalid_increment(self):
        # Increment is negative
        with self.assertRaises(ValueError):
            calculate_rebalance(False, -10, [100], [100])


    def test_percentages_sum_not_100(self):
        # Percentages do not sum to 100
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100], [50])


    def test_length_mismatch(self):
        # Mismatch in lengths of values and percentages
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100], [50, 50])


    def test_empty_lists(self):
        # Empty lists for values and percentages
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [], [])


    def test_non_numeric_values(self):
        # Non-numeric values in inputs
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, ["a", 100], [50, 50])
        with self.assertRaises(ValueError):
            calculate_rebalance(False, 100, [100, 100], ["b", 50])


if __name__ == "__main__":
    unittest.main()
