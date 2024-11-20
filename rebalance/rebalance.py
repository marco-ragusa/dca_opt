"""Core functions for portfolio rebalancing calculations."""


def calculate_only_buy(rebalances, increment):
    """
    Redistribute the increment proportionally among positive rebalances.

    Args:
        rebalances (list[float]): List of rebalance values.
        increment (float): Value to distribute among positive rebalances.

    Returns:
        list[float]: Adjusted rebalances with only positive increments.
    """
    positive_rebalances = [max(0, r) for r in rebalances]
    total_positive = sum(positive_rebalances)

    if total_positive == 0:
        return [0] * len(rebalances)

    return [
        (r / total_positive) * increment for r in positive_rebalances
    ]


def calculate_rebalance(only_buy, increment, values, percentages):
    """
    Calculate portfolio rebalances based on target percentages.

    Args:
        only_buy (bool): Flag to restrict rebalancing to positive adjustments.
        increment (float): Amount available for rebalancing.
        values (list[float]): Current values of portfolio holdings.
        percentages (list[float]): Target allocation percentages.

    Returns:
        list[float]: Adjusted rebalance values for each asset.
    """
    # Calculate the total target portfolio value after increment
    total_value = sum(values) + increment

    # Calculate rebalances as the difference between target and current values
    rebalances = [
        (total_value * (p / 100)) - v for p, v in zip(percentages, values)
    ]

    # Adjust rebalances for only_buy scenario
    adjusted_rebalances = (
        calculate_only_buy(rebalances, increment)
        if only_buy
        else rebalances
    )

    return [round(r, 2) for r in adjusted_rebalances]


def main():
    """Main function for local tests only"""
    increment = 100
    values = [0, 40, 100, 100]
    percentages = [60, 20, 10, 10]

    only_buy = False
    print(calculate_rebalance(only_buy, increment, values, percentages))
    # [204.0, 28.0, -66.0, -66.0]

    only_buy = True
    print(calculate_rebalance(only_buy, increment, values, percentages))
    # [87.93, 12.07, 0.0, 0.0]


if __name__ == "__main__":
    main()
