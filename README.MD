# DCA OPT

**DCA OPT** optimises a Dollar Cost Averaging investment strategy by computing
how many shares of each asset to buy when periodically investing a fixed amount,
while keeping the portfolio as close as possible to the desired target allocation.

---

## How it Works

1. **Load** your portfolio from a JSON config file.
2. **Fetch** the latest closing prices from Yahoo Finance (single batch request).
3. **Calculate** optimal rebalance amounts based on target percentages.
4. **Subtract** broker fees (never resulting in a negative purchase).
5. **Convert** currency amounts to whole share quantities (floor division).
6. **Redistribute** any leftover change among underweight assets.
7. **Print** the result sorted and filtered as requested.

---

## Project Structure

```
dca_opt/
├── dca_opt.py                 # CLI entry point
├── portfolio_example.json     # Example portfolio configuration
├── requirements.txt
│
├── models/
│   └── portfolio.py           # Asset + Portfolio dataclasses with validation
│
├── market_data/
│   └── market_data.py         # Batch price fetching via yfinance
│
├── rebalance/
│   ├── rebalance.py           # Core rebalancing calculations
│   └── test_rebalance.py      # Unit tests
│
└── utils/
    └── utils.py               # pretty_print, secure_division
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Portfolio Configuration

Create a JSON file following this schema:

```json
{
    "only_buy": true,
    "increment": 1000,
    "portfolio": [
        {
            "ticker": "VWCE.DE",
            "desired_percentage": 60,
            "shares": 10,
            "fees": 1.50
        },
        {
            "ticker": "VAGF.DE",
            "desired_percentage": 40,
            "shares": 5,
            "fees": 1.50
        }
    ]
}
```

| Field                | Type    | Description                                                  |
|----------------------|---------|--------------------------------------------------------------|
| `only_buy`           | bool    | If `true`, never sell — redistribute increment among underweight assets only |
| `increment`          | float   | Cash to invest this period (e.g. monthly savings)            |
| `ticker`             | string  | Yahoo Finance ticker symbol                                  |
| `desired_percentage` | float   | Target allocation weight (all assets must sum to **100**)    |
| `shares`             | float   | Shares currently held                                        |
| `fees`               | float   | Broker fee per transaction (deducted from rebalance amount)  |

---

## Usage

```bash
# Use the default portfolio_example.json
python dca_opt.py

# Specify a custom portfolio file
python dca_opt.py --portfolio my_portfolio.json

# Sort results by buy quantity, descending
python dca_opt.py --portfolio my_portfolio.json --sort buy --desc
```

### CLI Arguments

| Argument      | Default                     | Description                                          |
|---------------|-----------------------------|------------------------------------------------------|
| `--portfolio` | `portfolio_example.json`    | Path to the JSON portfolio configuration file        |
| `--sort`      | `ticker_price`              | Field to sort output by (`id`, `ticker`, `ticker_price`, `current_percentage`, `desired_percentage`, `buy`) |
| `--desc`      | *(flag, off by default)*    | Sort in descending order                             |

---

## Example Output

```json
{
    "results": [
        {
            "id": 0,
            "ticker": "VWCE.DE",
            "current_percentage": 0.0,
            "desired_percentage": 60,
            "shares": 0,
            "rebalance": 600.0,
            "ticker_price": 118.42,
            "fees": 0,
            "buy": 5
        },
        {
            "id": 1,
            "ticker": "VAGF.DE",
            "current_percentage": 0.0,
            "desired_percentage": 40,
            "shares": 0,
            "rebalance": 400.0,
            "ticker_price": 23.18,
            "fees": 0,
            "buy": 17
        }
    ],
    "total_fees": 0,
    "change": 6.52
}
```

---

## Running Tests

```bash
python -m unittest rebalance/test_rebalance.py -v
```
