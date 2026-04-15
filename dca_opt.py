"""DCA OPT - Dollar Cost Averaging portfolio optimiser.

Reads a JSON portfolio configuration, fetches live prices, and computes the
optimal number of shares to buy for each asset to best approach the desired
allocation while investing a fixed periodic increment.

Usage:

    python dca_opt.py --portfolio portfolio_example.json [--sort ticker_price] [--desc]
"""

import argparse
import logging
from pathlib import Path

import market_data
import rebalance
import utils
from models import Portfolio

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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

    Steps:
        1. Fetch current market prices in a single batch request.
        2. Calculate each asset's current monetary value and allocation weight.
        3. Compute optimal rebalance amounts to approach target allocations.
        4. Subtract broker fees from each allocation; clamp to zero.
        5. Convert currency amounts to whole share counts via floor division.
        6. Redistribute leftover change among eligible underweight assets
           (only_buy mode only).
        7. Deduct executed broker fees from leftover change so that
           ``change`` reflects the true uninvested remainder.

    Args:
        portfolio: A fully validated Portfolio instance.

    Returns:
        A dict with keys:
            'results'    -- list of per-asset dicts (field 'allocated' holds
                            the fee-adjusted target amount for that asset),
            'total_fees' -- sum of fees paid for all executed purchases,
            'change'     -- leftover cash after shares and fees are deducted.
    """
    tickers = [a.ticker for a in portfolio.assets]
    desired_pcts = [a.desired_percentage for a in portfolio.assets]
    shares = [a.shares for a in portfolio.assets]
    fees = [a.fees for a in portfolio.assets]

    # 1. Fetch current prices (single batch network call)
    prices = market_data.get_prices(tickers)
    ticker_prices = [prices[t] for t in tickers]

    # 2. Current values and allocation weights
    values = [s * p for s, p in zip(shares, ticker_prices)]
    total_value = sum(values)
    current_pcts = [utils.secure_division(v * 100.0, total_value) for v in values]

    # 3. Optimal rebalance amounts (in portfolio currency)
    rebalance_amounts = rebalance.calculate_rebalance(
        portfolio.only_buy, portfolio.increment, values, desired_pcts
    )

    # 4. Subtract broker fees; clamp to zero to prevent negative purchases
    rebalance_amounts = [
        max(0.0, r - f) if r > 0 else r
        for r, f in zip(rebalance_amounts, fees)
    ]

    # 5. Convert to whole share counts
    buy_quantities: list[int] = [int(r // p) for r, p in zip(rebalance_amounts, ticker_prices)]

    # 6. Deduct fees before redistribution so that fee-reserved cash is never
    #    handed to redistribute_change (which would otherwise spend it on shares,
    #    pushing the final change negative).
    #    Note: redistribute_change only touches assets already scheduled for
    #    purchase (buy > 0), so total_fees is stable across redistribution.
    spent = sum(b * p for b, p in zip(buy_quantities, ticker_prices))
    total_fees = sum(f for f, b in zip(fees, buy_quantities) if b > 0)
    change = portfolio.increment - spent - total_fees

    # 7. Redistribute the true leftover change (only_buy mode only)
    if portfolio.only_buy:
        buy_quantities, change = rebalance.redistribute_change(
            buy_quantities, ticker_prices, current_pcts, desired_pcts, change
        )

    results = [
        {
            "id": i,
            "ticker": ticker,
            "current_percentage": cur_pct,
            "desired_percentage": des_pct,
            "shares": share,
            "allocated": alloc,
            "ticker_price": price,
            "fees": fee,
            "buy": qty,
        }
        for i, (ticker, cur_pct, des_pct, share, alloc, price, fee, qty) in enumerate(
            zip(tickers, current_pcts, desired_pcts, shares,
                rebalance_amounts, ticker_prices, fees, buy_quantities)
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
