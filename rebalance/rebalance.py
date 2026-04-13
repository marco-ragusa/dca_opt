"""Core functions for portfolio rebalancing calculations."""


def validate_inputs(
    values: list[float],
    percentages: list[float],
    increment: float,
) -> None:
    """Validate all inputs required for a rebalancing calculation.

    Args:
        values: Current monetary values of each portfolio holding.
        percentages: Target allocation percentages for each holding.
        increment: Additional cash amount available for investment.

    Raises:
        ValueError: If any input violates the expected constraints.
    """
    if not values or not percentages:
        raise ValueError("Values and percentages cannot be empty.")
    if not isinstance(increment, (int, float)) or increment < 0:
        raise ValueError(
            f"Increment must be a non-negative number, got {increment!r}."
        )
    if len(values) != len(percentages):
        raise ValueError(
            f"Values and percentages must have the same length "
            f"({len(values)} vs {len(percentages)})."
        )
    if not all(isinstance(v, (int, float)) for v in values):
        raise ValueError("All values must be numeric.")
    if not all(isinstance(p, (int, float)) for p in percentages):
        raise ValueError("All percentages must be numeric.")
    if round(sum(percentages), 2) != 100.0:
        raise ValueError(
            f"Percentages must sum to 100.00, got {sum(percentages):.2f}."
        )


def _compute_target_rebalances(
    values: list[float],
    percentages: list[float],
    total_value: float,
) -> list[float]:
    """Calculate how much each holding needs to change to reach its target allocation.

    Args:
        values: Current monetary values of each holding.
        percentages: Target allocation percentages.
        total_value: Target total portfolio value (current + increment).

    Returns:
        List of signed rebalance amounts; positive means buy, negative means sell.
    """
    return [(total_value * (p / 100.0)) - v for p, v in zip(percentages, values)]


def _redistribute_proportional_to_gap(
    values: list[float],
    percentages: list[float],
    increment: float,
) -> list[float]:
    """Distribute the increment proportionally to each asset's positive rebalance gap.

    Used in only_buy mode.

    For every asset the gap is computed as the distance between its current value
    and where it needs to be in the post-increment total portfolio:

        gap_i = (sum(values) + increment) * (target_i / 100) - value_i

    Negative gaps mean the asset is already overweight relative to the new total
    and receive zero new money. Positive gaps act as weights: an asset with a
    large gap receives a proportionally larger slice of the increment than one with
    a small gap. This provides a smooth gradient:

    - Heavily overweight assets have a large negative gap -> weight = 0.
    - Slightly overweight assets whose gap flips positive due to the new total
      receive a small but non-zero weight (not hard-excluded).
    - Heavily underweight assets have large positive gaps -> higher weight.

    Example - values [0, 40, 100, 100], targets [60, 20, 10, 10], increment 100:
    - Post-increment total = 340.
    - Gaps: A = +204, B = +28, C = -66, D = -66.
    - Total positive gap = 232.
    - A receives 100 * 204/232 = 87.93; B receives 100 * 28/232 = 12.07.

    Args:
        values: Current monetary value held in each asset.
        percentages: Target allocation percentages, aligned with values.
        increment: Total new cash to distribute.

    Returns:
        Allocation amounts per asset; overweight assets receive 0, underweight
        assets receive amounts summing exactly to increment.
    """
    total_value = sum(values) + increment
    gaps = [(total_value * p / 100.0) - v for p, v in zip(percentages, values)]

    total_positive = sum(g for g in gaps if g > 0)
    if total_positive == 0:
        return [0.0] * len(values)

    return [
        increment * (g / total_positive) if g > 0 else 0.0
        for g in gaps
    ]


def calculate_rebalance(
    only_buy: bool,
    increment: float,
    values: list[float],
    percentages: list[float],
) -> list[float]:
    """Calculate the optimal rebalance amounts for each portfolio holding.

    Args:
        only_buy: When True, disallow selling. The increment is distributed
            only among underweight holdings proportional to their gap.
        increment: Additional cash being invested this period.
        values: Current monetary value held in each asset.
        percentages: Target allocation percentage for each asset (must sum to 100).

    Returns:
        Currency amounts to invest/divest per holding, rounded to 2 decimal places.
        In only_buy mode all amounts are >= 0.
    """
    validate_inputs(values, percentages, increment)

    if only_buy:
        rebalances = _redistribute_proportional_to_gap(values, percentages, increment)
    else:
        total_value = sum(values) + increment
        rebalances = _compute_target_rebalances(values, percentages, total_value)

    return [round(r, 2) for r in rebalances]


def redistribute_change(
    buy_quantities: list[float],
    ticker_prices: list[float],
    current_percentages: list[float],
    desired_percentages: list[float],
    change: float,
) -> tuple[list[float], float]:
    """Redistribute leftover cash from discrete share purchases.

    After converting currency amounts to whole share counts via floor division,
    there is typically some cash left over. This function allocates that change
    to eligible assets, prioritising those furthest below their target allocation.

    Only assets that already have a non-zero buy quantity are eligible, preventing
    unintended purchases in assets intentionally excluded from the current round.

    Algorithm:
        This function implements a greedy algorithm for the Unbounded Integer Knapsack
        Problem adapted to portfolio underweight prioritisation (sometimes called the
        Greedy Assignment by Underweight Priority method in portfolio rebalancing).

    Decision variables:
        x_i  in  Z≥0  -- extra shares to buy for asset i
        q_i^0         -- initial whole-share buy quantity for asset i
        p_i           -- price per share for asset i
        c             -- leftover cash (change)

    Objective (implicitly maximised):
        Maximise  Σ w_i · x_i,   w_i ∝ (desired_i + ε) / current_i

        A higher w_i means the asset is further below its target allocation.

    Constraints:
        Capacity:    Σ p_i · x_i ≤ c
        Eligibility: x_i = 0 whenever q_i^0 ≤ 0 (only buy what was already scheduled)
        Integrality: x_i ∈ Z≥0

    Formal algorithm (4 steps):
        1. Compute priority ratio  k_i = current_i / (desired_i + ε)  for every asset.
           A low ratio means the asset is heavily underweight (high urgency).
        2. Sort asset indices in ascending order of k_i.
        3. For each index i in that order:
               if q_i^0 > 0:  x_i = floor(c_remaining / p_i)
                              c_remaining -= x_i · p_i
               else:          x_i = 0
        4. Return updated quantities and c_remaining (rounded to 2 decimal places).

    Complexity: O(n log n) dominated by the sort in step 2.

    Args:
        buy_quantities: Whole share counts to purchase per asset.
        ticker_prices: Current price per share for each asset.
        current_percentages: Current portfolio weight of each asset (%).
        desired_percentages: Target portfolio weight of each asset (%).
        change: Leftover cash to allocate.

    Returns:
        A tuple of (updated buy quantities, remaining unallocated change).
    """
    # Step 1 – Compute priority ratio k_i = current_i / (desired_i + ε).
    # ε = 0.01 avoids division-by-zero when desired_i = 0.
    # A lower k_i means the asset is more underweight relative to its target.
    epsilon = 0.01
    priorities = [
        current_percentages[i] / (desired_percentages[i] + epsilon)
        for i in range(len(buy_quantities))
    ]

    # Step 2 – Sort asset indices ascending by k_i (most underweight first).
    sorted_indices = sorted(range(len(buy_quantities)), key=lambda i: priorities[i])

    # Step 3 – Greedily assign extra shares to each eligible asset.
    # x_i = floor(c_remaining / p_i); then reduce remaining change by x_i · p_i.
    updated = list(buy_quantities)
    remaining = change
    for i in sorted_indices:
        if updated[i] <= 0:             # eligibility: skip assets not in this buy round
            continue
        x_i = remaining // ticker_prices[i]     # floor(c_remaining / p_i)
        remaining -= x_i * ticker_prices[i]
        updated[i] += x_i

    # Step 4 – Return updated quantities and final remaining change.
    return updated, round(remaining, 2)
