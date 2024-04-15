"""Module that provides util functions."""

import json


def pretty_print(results: dict, sort: str = "id", desc: bool = False, only_buy: bool = False):
    """
    Prints formatted results with optional sorting and filtering.

    Args:
    - results (dict): Dictionary containing results to be printed.
    - sort (str): Key to sort results by (default is "id").
    - desc (bool): Flag indicating whether to sort in descending order (default is False).
    - only_buy (bool): Flag indicating whether to filter only buy results (default is False).

    Returns:
    - None
    """
    # Sort by in descending order if True
    results["results"] = sorted(results["results"], key=lambda x: x[sort], reverse=desc)
    # Filter only buy if True
    if only_buy:
        results["results"] = [result for result in results["results"] if result["buy"] > 0]

    print(json.dumps(results, indent=4))


def data_rearrange(data: dict) -> dict:
    """
    Rearrange data dictionary containing portfolio information into individual lists.

    Args:
    - data (dict): Dictionary containing portfolio information including 'only_buy', 'increment',
      'portfolio' (a list of dictionaries with 'ticker', 'desired_percentage', 'shares', 'fees').

    Returns:
    - dict: A dict containing unpacked lists including 'only_buy' flag, 'increment' value,
      'tickers', 'desired_percentage', 'shares' and 'fees'.
    """
    return {
        "only_buy": data["only_buy"],
        "increment": data["increment"],
        "tickers": [item["ticker"] for item in data["portfolio"]],
        "desired_percentage": [item["desired_percentage"] for item in data["portfolio"]],
        "shares": [item["shares"] for item in data["portfolio"]],
        "fees": [item["fees"] for item in data["portfolio"]],
    }


def secure_division(n, d):
    """
    Performs a secure division operation.

    Parameters:
    - n (float): The numerator.
    - d (float): The denominator.

    Returns:
    - float: The result of the division (n / d), or 0 if the denominator is 0.
    """
    return n / d if d else 0
