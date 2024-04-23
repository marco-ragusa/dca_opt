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


def data_unpack(data: dict) -> dict:
    """
    Unpack data dictionary containing portfolio information into individual lists.

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


def create_results(data: dict) -> list:
    """
    Generate a list of dictionaries containing financial data for each ticker.

    Args:
        data (dict): A dictionary containing financial data for various tickers.

    Returns:
        list: A list of dictionaries containing financial data for each ticker.
    """
    results = []
    for i, ticker in enumerate(data["tickers"]):
        results.append({
            "id": i,
            "ticker": ticker,
            "current_percentage": round(data["current_percentages"][i], 2),
            "desired_percentage": data["desired_percentage"][i],
            "shares": data["shares"][i],
            "rebalance": data["rebalances"][i],
            "ticker_price": round(data["ticker_prices"][i], 2),
            "fees": data["fees"][i],
            "buy": data["buy"][i]
        })

    return results


def calculate_change(increment: float, results: list) -> float:
    """
    Calculate the change based on the given increment and results.

    Parameters:
        increment (float): The total amount of change to be distributed.
        results (list): A list of dictionaries representing assets with their
            buy quantity and ticker price.

    Returns:
        float: The change calculated after subtracting the total value of
            purchased assets from the increment.
    """
    total = 0
    for result in results:
        total += result["buy"] * result["ticker_price"]

    change = increment - total

    return change


def redistribute_change(results, change):
    """
    Redistribute the given change among the assets in the provided results.

    Parameters:
        results (list): A list of dictionaries representing assets with their
            current percentage, desired percentage, buy quantity, ticker price,
            and id.
        change (float): The amount of change to be redistributed.

    Returns:
        tuple: A tuple containing the updated results after redistributing the
            change among assets and the remaining change rounded to two
            decimal places.
    """
    # Add 0.01 to avoid division by zero and improve sorting
    results.sort(key=lambda x: x["current_percentage"] / (x["desired_percentage"] + 0.01))

    # Redistribute the change between assets
    for i, result in enumerate(results):
        # Check if you could buy with rebalance
        if result["buy"] > 0:
            buy_quantity = change // result["ticker_price"]
            change -= buy_quantity * result["ticker_price"]
            results[i]["buy"] += buy_quantity

    # Sort by id
    results.sort(key=lambda x: x["id"], reverse=True)

    return results, round(change, 2)


def data_pack(data: dict) -> dict:
    """
    Packs data into a dictionary containing results and change.

    Args:
        data (dict): A dictionary containing input data.

    Returns:
        dict: A dictionary containing packed data.
            Keys:
                - "results" (list): Initial results list.
                - "change" (float): Calculated change value.
    """
    # Create initial results list
    results = create_results(data)

    change = calculate_change(data["increment"], results)

    # Improve change distribution for only_buy
    if data["only_buy"]:
        results, change = redistribute_change(results, change)
    
    total_fees = sum(fees for fees, buy in zip(data["fees"], data["buy"]) if buy != 0)

    return { "results": results, "total_fees": total_fees, "change": change }


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
