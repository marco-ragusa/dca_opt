"""DCA OPT."""

import portfolio_example as pf
# import portfolios.portfolio as pf

import market_data
import rebalance
import utils


def create_result(data: dict) -> list:
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
            "fee": data["fees"][i],
            "buy": data["rebalances"][i] // data["ticker_prices"][i]
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


def dca_opt(portfolio_data):
    """DCA OPT function."""
    # Rearrange data into dict format for processing
    data = utils.data_rearrange(portfolio_data)

    # Get actual price
    data["ticker_prices"] = [market_data.get_price(t) for t in data["tickers"]]

    # Prices owned per ticker
    data["values"] = [s * tp for s, tp in zip(data["shares"], data["ticker_prices"])]

    # Current percentage per ticker
    sum_values = sum(data["values"])
    data["current_percentages"] = [
        # Use secure_division to avoid division by zero
        utils.secure_division((value * 100), sum_values) for value in data["values"]
    ]

    # Get rebalanced value
    data["rebalances"] = rebalance.calculate_rebalance(
        data["only_buy"], data["increment"], data["values"], data["desired_percentage"]
    )

    # Remove fees from rebalances
    for i, _ in enumerate(data["rebalances"]):
        if data["rebalances"][i] != 0:
            data["rebalances"][i] -= data["fees"][i]

    create_result(data)

    # Create initial result dict
    results = create_result(data)

    change = calculate_change(data["increment"], results)

    # Improve change distribution for only_buy
    if data["only_buy"]:
        results, change = redistribute_change(results, change)

    return { "results": results, "change": change }


if __name__ == "__main__":
    utils.pretty_print(
        dca_opt(pf.data),
        sort="ticker_price",
        desc=True,
        only_buy=pf.data["only_buy"]
    )
