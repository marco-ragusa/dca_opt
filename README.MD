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
6. **Redistribute** any leftover change among eligible assets — either via a
   fast greedy heuristic (default) or an exact knapsack DP that maximises
   cash usage (opt-in via `optimal_redistribute`).
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
    "optimal_redistribute": false,
    "portfolio": [
        {
            "ticker": "VWCE.DE",
            "desired_percentage": 60,
            "shares": 10,
            "fees": 0.5,
            "percentage_fee": true
        },
        {
            "ticker": "VAGF.DE",
            "desired_percentage": 40,
            "shares": 5,
            "fees": 1.50,
            "percentage_fee": false
        }
    ]
}
```

| Field                   | Type    | Description                                                  |
|-------------------------|---------|--------------------------------------------------------------|
| `only_buy`              | bool    | If `true`, never sell — redistribute increment among underweight assets only |
| `increment`             | float   | Cash to invest this period (e.g. monthly savings)            |
| `optimal_redistribute`  | bool    | *(optional, default `false`)* Use the exact knapsack DP for the leftover-change step |
| `ticker`                | string  | Yahoo Finance ticker symbol                                  |
| `desired_percentage`    | float   | Target allocation weight (all assets must sum to **100**)    |
| `shares`                | float   | Shares currently held                                        |
| `percentage_fee`        | bool    | *(optional, default `false`)* `false` — flat amount per trade; `true` — % of rebalance allocation |
| `fees`                  | float   | Broker fee: absolute amount when `percentage_fee` is `false`, or percentage 0–100 when `true` |

### Fee types

| `percentage_fee` | `fees` meaning        | Example                          |
|------------------|-----------------------|----------------------------------|
| `false`          | Flat amount per trade | `"fees": 1.50` → €1.50 deducted  |
| `true`           | % of rebalance amount | `"fees": 0.5` → 0.5 % deducted   |

For percentage fees the effective deduction is computed as:

```
effective_fee = rebalance_allocation × fees / 100
net_investable = rebalance_allocation − effective_fee
```

The `fees` field in the output always shows the **effective absolute fee** actually paid for that transaction (i.e. the converted amount for percentage fees).

### The `optimal_redistribute` Flag

The final redistribution step can strand cash when share prices do not evenly
divide the leftover.  Two algorithms are available:

| Algorithm                        | Trade-off                                                                                                                              |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Greedy** (default)             | O(n log n); fast but can leave cash unspent if the most-underweight asset's price does not divide the change evenly                    |
| **Optimal knapsack DP** (opt-in) | O(n × c) in integer cents; exact max-spent with a deterministic tiebreaker that prefers more underweight assets                        |

Both algorithms run in either `only_buy` mode.  The greedy path is also used
as a fallback whenever `change_cents > MAX_CENTS` (~$10,000), regardless of
which algorithm is configured, to bound memory and time usage.

When `only_buy=true` the DP additionally **excludes already-overweight assets**
from the candidate set: the buy-only promise "never push an asset further above
its target" is preserved even during redistribution.  A small amount of leftover
cash is preferred to pushing an overweight asset higher.

When `only_buy=false` the DP runs over every asset with `buy > 0` and purely
maximises cash usage (any overshoot can be corrected by selling on the next
cycle).

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
            "allocated": 600.0,
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
            "allocated": 400.0,
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
# Unit tests for the rebalance module (calculate_rebalance + both redistribution algorithms)
python -m unittest rebalance.test_rebalance -v

# Integration tests for the full pipeline (dca_opt.py, flag wiring, edge cases)
python -m unittest test_dca_opt -v

# Everything at once
python -m unittest discover -v
```
