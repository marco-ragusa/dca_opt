"""DCA OPT."""

import portfolio_example as pf
# import portfolios.portfolio as pf

import market_data
import rebalance
import utils


def dca_opt(portfolio_data):
    """DCA OPT function."""
    # Unpack data into dict format for processing
    data = utils.data_unpack(portfolio_data)

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

    # Pack and return the result data
    return utils.data_pack(data)


if __name__ == "__main__":
    utils.pretty_print(
        dca_opt(pf.data),
        sort="ticker_price",
        desc=True,
        only_buy=pf.data["only_buy"]
    )
