"""DCA OPT - Dollar Cost Averaging portfolio optimiser.

Reads a JSON portfolio configuration, fetches live prices, and computes the
optimal number of shares to buy for each asset to best approach the desired
allocation while investing a fixed periodic increment.

Usage:

    python dca_opt.py --portfolio portfolio_example.json [--sort ticker_price] [--desc]
"""

import argparse
import dataclasses
import logging
from pathlib import Path

import market_data
import rebalance
import utils
from models import AssetResult, Portfolio

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _effective_fee(fee: float, percentage_fee: bool, rebalance_amount: float) -> float:
    """Return the absolute fee for a single transaction."""
    if percentage_fee:
        return rebalance_amount * fee / 100.0
    return fee


_SORT_CHOICES = [
    "id",
    "ticker",
    "ticker_price",
    "current_percentage",
    "desired_percentage",
    "buy",
]


def dca_opt(portfolio: Portfolio) -> dict:
    """Compute optimal buy quantities for each asset in a portfolio.

    Args:
        portfolio: A fully validated Portfolio instance.

    Returns:
        A dict with keys 'results' (list of per-asset dicts), 'total_fees', 'change'.
    """
    tickers = [a.ticker for a in portfolio.assets]
    desired_pcts = [a.desired_percentage for a in portfolio.assets]
    shares = [a.shares for a in portfolio.assets]

    prices = market_data.get_prices(tickers)
    ticker_prices = [round(prices[t], 2) for t in tickers]

    for ticker, price in zip(tickers, ticker_prices):
        if price <= 0:
            raise ValueError(f"Invalid price for '{ticker}': {price}. Prices must be positive.")

    values = [s * p for s, p in zip(shares, ticker_prices)]
    total_value = sum(values)
    current_pcts = [utils.secure_division(v * 100.0, total_value) for v in values]

    rebalance_amounts = rebalance.calculate_rebalance(
        portfolio.only_buy, portfolio.increment, values, desired_pcts
    )

    effective_fees = [
        _effective_fee(a.fees, a.percentage_fee, r) if r > 0 else 0.0
        for a, r in zip(portfolio.assets, rebalance_amounts)
    ]
    rebalance_amounts = [
        max(0.0, r - ef) if r > 0 else r
        for r, ef in zip(rebalance_amounts, effective_fees)
    ]

    buy_quantities: list[int] = [int(r // p) for r, p in zip(rebalance_amounts, ticker_prices)]

    spent = sum(b * p for b, p in zip(buy_quantities, ticker_prices))
    total_fees = sum(ef for ef, b in zip(effective_fees, buy_quantities) if b > 0)
    change = round(portfolio.increment - spent - total_fees, 2)

    if portfolio.optimal_redistribute:
        buy_quantities, change = rebalance.redistribute_change_optimal(
            portfolio.only_buy,
            buy_quantities, ticker_prices,
            current_pcts, desired_pcts, change,
        )
    else:
        buy_quantities, change = rebalance.redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

    results = [
        dataclasses.asdict(AssetResult(
            id=i,
            ticker=ticker,
            current_percentage=cur_pct,
            desired_percentage=des_pct,
            shares=share,
            allocated=alloc,
            ticker_price=price,
            fees=ef if qty > 0 else 0.0,
            buy=qty,
        ))
        for i, (ticker, cur_pct, des_pct, share, alloc, price, ef, qty) in enumerate(
            zip(tickers, current_pcts, desired_pcts, shares,
                rebalance_amounts, ticker_prices, effective_fees, buy_quantities)
        )
    ]

    return {"results": results, "total_fees": total_fees, "change": change}


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dca_opt",
        description="DCA OPT - Dollar Cost Averaging portfolio optimiser.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=Path("portfolio_example.json"),
        metavar="FILE",
        help="Path to the JSON portfolio configuration file.",
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="ticker_price",
        choices=_SORT_CHOICES,
        help="Field to sort results by.",
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        help="Sort results in descending order.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    portfolio = Portfolio.from_json(args.portfolio)
    output = dca_opt(portfolio)
    utils.pretty_print(output, sort=args.sort, desc=args.desc, only_buy=portfolio.only_buy)
