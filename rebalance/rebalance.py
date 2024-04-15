"""Module for rebalancing a portfolio."""

def calculate_only_buy(rebalances, increment) -> list[float]:
    """
    Calculate the incremental values for positive rebalances only.

    Args:
    - rebalances (list[float]): List of rebalance values.
    - increment (float): Incremental value to distribute among positive rebalances.

    Returns:
    - list[float]: List of incremental values for positive rebalances.
    """
    # Replace negative rebalance with zero
    rebalances = [max(rebalance, 0) for rebalance in rebalances]

    # Sum only positive rebalances
    rebalances_sum = sum(rebalances)

    # Calculate the percentage of each positive rebalance relative to the sum of positive rebalances
    rebalances_percentages = []
    for rebalance in rebalances:
        rebalances_percentages.append((rebalance / rebalances_sum) * 100)

    # Distribute the increment based on the positive rebalance percentages
    incremental_rebalances = []
    for percentage in rebalances_percentages:
        incremental_rebalances.append((percentage * increment) / 100)

    return incremental_rebalances


def calculate_rebalance(only_buy, increment, values, percentages) -> list[float]:
    """
    Calculate rebalances based on given values and percentages.

    Args:
    - only_buy (bool): Flag indicating whether to consider only positive rebalances.
    - increment (float): Incremental value to distribute among rebalances.
    - values (list[float]): Initial values.
    - percentages (list[float]): Desired percentages for rebalancing.

    Returns:
    - list[float]: List of rebalance values.
    """
    # Calculate the total sum of initial values and the increment
    total_sum = sum(values) + increment

    # Calculate the rebalance for each value based on the desired percentages
    rebalances = []
    for percentage, value in zip(percentages, values):
        rebalances.append((total_sum * (percentage / 100)) - value)

    if only_buy:
        rebalances = calculate_only_buy(rebalances, increment)

    return [round(rebalance, 2) for rebalance in rebalances]


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
