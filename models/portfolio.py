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


@dataclass
class Portfolio:
    """Represents a complete investment portfolio configuration."""

    only_buy: bool
    increment: float
    assets: list[Asset]

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
                "portfolio": [
                    {
                        "ticker": "VWCE.DE",
                        "desired_percentage": 60,
                        "shares": 10,
                        "fees": 1.5
                    }
                ]
            }

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

        try:
            assets = [
                Asset(
                    ticker=str(item["ticker"]),
                    desired_percentage=float(item["desired_percentage"]),
                    shares=float(item["shares"]),
                    fees=float(item["fees"]),
                )
                for item in raw["portfolio"]
            ]
            return cls(
                only_buy=bool(raw["only_buy"]),
                increment=float(raw["increment"]),
                assets=assets,
            )
        except KeyError as exc:
            raise ValueError(
                f"Missing required field in portfolio JSON: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid value in portfolio JSON: {exc}"
            ) from exc
