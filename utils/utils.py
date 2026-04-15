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


def _format_floats(obj: object) -> object:
    """Recursively replace every float with its ``{:.2f}`` string representation.

    Applied only when building the display output; internal calculation values
    are never modified.

    Args:
        obj: Any JSON-serialisable object (dict, list, float, int, str, …).

    Returns:
        A new object of the same shape with floats formatted to 2 decimal places.
    """
    if isinstance(obj, float):
        return f"{obj:.2f}"
    if isinstance(obj, dict):
        return {k: _format_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_format_floats(v) for v in obj]
    return obj


def pretty_print(
    output: dict,
    sort: str = "id",
    desc: bool = False,
    only_buy: bool = False,
) -> None:
    """Print the DCA optimisation results as formatted JSON.

    Floats are formatted to 2 decimal places using ``{:.2f}`` at display time
    only; no rounding is applied to the underlying values.

    Args:
        output: The result dict produced by dca_opt, containing at minimum
            a 'results' list of per-asset result dicts.
        sort: Key within each result dict to sort by (default 'id').
        desc: When True, sort in descending order.
        only_buy: When True, exclude assets with a buy quantity of zero.
    """
    # Sort and filter on raw values before formatting.
    results = sorted(output["results"], key=lambda r: r[sort], reverse=desc)

    if only_buy:
        results = [r for r in results if r["buy"] > 0]

    display = {**output, "results": results}
    print(json.dumps(_format_floats(display), indent=4))
