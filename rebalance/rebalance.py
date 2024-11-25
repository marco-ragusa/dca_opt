"""Core functions for portfolio rebalancing calculations."""

def validate_inputs(values, percentages, increment):
    """
    Validate inputs for rebalancing calculations.

    Args:
        values (list[float]): Current values of portfolio holdings.
        percentages (list[float]): Target allocation percentages.
        increment (float): Amount available for rebalancing.

    Raises:
        ValueError: If any input is invalid.
    """
    if not isinstance(increment, (int, float)) or increment < 0:
        raise ValueError("Increment must be a non-negative number.")
    if len(values) != len(percentages):
        raise ValueError("Values and percentages must have the same length.")
    if not all(isinstance(v, (int, float)) for v in values):
        raise ValueError("All values must be numbers.")
    if not all(isinstance(p, (int, float)) for p in percentages):
        raise ValueError("All percentages must be numbers.")
    if round(sum(percentages), 2) != 100:
        raise ValueError("Percentages must sum up to 100.")


def compute_target_rebalances(values, percentages, total_value):
    """
    Calculate target rebalances based on the desired percentages.

    Args:
        values (list[float]): Current values of portfolio holdings.
        percentages (list[float]): Target allocation percentages.
        total_value (float): Total portfolio value after increment.

    Returns:
        list[float]: Target rebalances for each asset.
    """
    return [(total_value * (p / 100)) - v for p, v in zip(percentages, values)]


def redistribute_positive_rebalances(rebalances, increment):
    """
    Redistribute the increment proportionally among positive rebalances.

    Args:
        rebalances (list[float]): List of rebalance values.
        increment (float): Value to distribute among positive rebalances.

    Returns:
        list[float]: Adjusted rebalances with only positive increments.
    """
    positive_rebalances = [r for r in rebalances if r > 0]
    total_positive = sum(positive_rebalances)

    if total_positive == 0:
        return [0] * len(rebalances)

    factor = increment / total_positive
    return [r * factor if r > 0 else 0 for r in rebalances]


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
    # Validate inputs
    validate_inputs(values, percentages, increment)

    # Calculate the total target portfolio value after increment
    total_value = sum(values) + increment

    # Calculate initial rebalances
    rebalances = compute_target_rebalances(values, percentages, total_value)

    # Adjust rebalances for only_buy scenario
    adjusted_rebalances = (
        redistribute_positive_rebalances(rebalances, increment)
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

    ###

    increment = 0
    values = [0, 0, 100, 100]
    percentages = [60, 20, 10, 10]

    only_buy = False
    print(calculate_rebalance(only_buy, increment, values, percentages))
    # [120.0, 120.0, -80.0, -80.0]

    only_buy = True
    print(calculate_rebalance(only_buy, increment, values, percentages))
    # [0.0, 0.0, 0.0, 0.0]


if __name__ == "__main__":
    main()
