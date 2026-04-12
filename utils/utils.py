"""General-purpose utility functions."""

import json


def secure_division(numerator: float, denominator: float) -> float:
    """Perform division, returning 0 when the denominator is falsy.

    Args:
        numerator: The dividend.
        denominator: The divisor.

    Returns:
        numerator / denominator, or 0 if denominator is zero.
    """
    return numerator / denominator if denominator else 0.0


def pretty_print(
    output: dict,
    sort: str = "id",
    desc: bool = False,
    only_buy: bool = False,
) -> None:
    """Print the DCA optimisation results as formatted JSON.

    Args:
        output: The result dict produced by dca_opt, containing at minimum
            a 'results' list of per-asset result dicts.
        sort: Key within each result dict to sort by (default 'id').
        desc: When True, sort in descending order.
        only_buy: When True, exclude assets with a buy quantity of zero.
    """
    results = sorted(output["results"], key=lambda r: r[sort], reverse=desc)

    if only_buy:
        results = [r for r in results if r["buy"] > 0]

    display = {**output, "results": results}
    print(json.dumps(display, indent=4))
