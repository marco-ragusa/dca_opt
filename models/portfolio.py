"""Portfolio domain models with built-in validation."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Asset:
    """Represents a single investable asset within a portfolio."""

    ticker: str
    desired_percentage: float
    shares: float
    fees: float
    percentage_fee: bool = False

    def __post_init__(self) -> None:
        if not self.ticker or not self.ticker.strip():
            raise ValueError("Asset ticker cannot be empty.")
        if not (0 < self.desired_percentage <= 100):
            raise ValueError(
                f"Asset '{self.ticker}': desired_percentage must be between 0 and 100 "
                f"(exclusive/inclusive), got {self.desired_percentage}."
            )
        if self.shares < 0:
            raise ValueError(
                f"Asset '{self.ticker}': shares cannot be negative, got {self.shares}."
            )
        if self.fees < 0:
            raise ValueError(
                f"Asset '{self.ticker}': fees cannot be negative, got {self.fees}."
            )
        if self.percentage_fee and self.fees > 100:
            raise ValueError(
                f"Asset '{self.ticker}': percentage fee cannot exceed 100, "
                f"got {self.fees}."
            )


@dataclass
class Portfolio:
    """Represents a complete investment portfolio configuration."""

    only_buy: bool
    increment: float
    assets: list[Asset]
    optimal_redistribute: bool = False

    def __post_init__(self) -> None:
        if self.increment < 0:
            raise ValueError(
                f"Increment must be a non-negative number, got {self.increment}."
            )
        if not self.assets:
            raise ValueError("Portfolio must contain at least one asset.")
        total_pct = sum(a.desired_percentage for a in self.assets)
        if round(total_pct, 2) != 100.0:
            raise ValueError(
                f"Asset desired_percentages must sum to 100.00, got {total_pct:.2f}."
            )

    @classmethod
    def from_json(cls, path: str | Path) -> "Portfolio":
        """Load and validate a Portfolio from a JSON configuration file.

        The JSON must follow this schema:

            {
                "only_buy": true,
                "increment": 1000,
                "optimal_redistribute": false,
                "portfolio": [
                    {
                        "ticker": "VWCE.DE",
                        "desired_percentage": 60,
                        "shares": 10,
                        "fees": 1.5,
                        "percentage_fee": false
                    }
                ]
            }

        ``percentage_fee`` is optional and defaults to ``false`` (backwards-compatible).
        Set it to ``true`` to express the fee as a percentage of the rebalance
        allocation for that asset (0–100).

        The ``optimal_redistribute`` field is optional and defaults to ``False``
        (backwards-compatible).  When ``True`` the pipeline uses the exact
        knapsack-based redistribution in
        :func:`rebalance.redistribute_change_optimal` instead of the greedy
        :func:`rebalance.redistribute_change`.

        Args:
            path: Path to the JSON portfolio configuration file.

        Returns:
            A fully validated Portfolio instance.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            ValueError: If any required field is missing or any value is invalid.
        """
        json_path = Path(path)
        if not json_path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {json_path.resolve()}")

        with json_path.open(encoding="utf-8") as fh:
            raw = json.load(fh)

        def _require_bool(value: object, field: str) -> bool:
            if not isinstance(value, bool):
                raise ValueError(
                    f"'{field}' must be a JSON boolean (true/false), "
                    f"got {type(value).__name__!r}."
                )
            return value

        try:
            assets = [
                Asset(
                    ticker=str(item["ticker"]),
                    desired_percentage=float(item["desired_percentage"]),
                    shares=float(item["shares"]),
                    fees=float(item["fees"]),
                    percentage_fee=_require_bool(
                        item.get("percentage_fee", False), "percentage_fee"
                    ),
                )
                for item in raw["portfolio"]
            ]
            return cls(
                only_buy=_require_bool(raw["only_buy"], "only_buy"),
                increment=float(raw["increment"]),
                assets=assets,
                optimal_redistribute=_require_bool(
                    raw.get("optimal_redistribute", False), "optimal_redistribute"
                ),
            )
        except KeyError as exc:
            raise ValueError(
                f"Missing required field in portfolio JSON: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid value in portfolio JSON: {exc}"
            ) from exc
