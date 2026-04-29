# Backend

FastAPI application that exposes `POST /v1/rebalance`. Accepts a portfolio
configuration and returns per-asset buy quantities, fees, and leftover change.

## Structure

```
app/
├── main.py                        # FastAPI app entry point
├── api/
│   ├── deps.py                    # Dependency injection (market provider)
│   └── v1/routes/
│       ├── rebalance.py           # POST /v1/rebalance
│       └── health.py              # GET /v1/health, GET /v1/ready
├── schemas/
│   ├── request.py                 # RebalanceRequest, AssetIn (Pydantic v2)
│   └── result.py                  # RebalanceResponse, AssetResultOut
├── services/
│   └── rebalance_service.py       # Core orchestration logic
├── market_data/
│   ├── base.py                    # AbstractMarketDataProvider (ABC)
│   ├── yfinance_provider.py       # yfinance batch + fallback retry
│   ├── cache.py                   # AbstractCache + LocalCache (in-memory, TTL)
│   ├── redis_cache.py             # RedisCache (lazy import, per cluster)
│   └── cached_provider.py         # CachedMarketDataProvider (decorator)
├── core/
│   ├── config.py                  # Settings via pydantic-settings
│   ├── exceptions.py              # Custom exception handlers
│   ├── formatting.py              # Shared numeric truncation helper
│   └── log_config.py              # Logging setup
└── rebalance/
    └── rebalance.py               # Core algorithms (DP + greedy)

tests/
├── conftest.py                    # Shared fixtures (mock provider, test client)
├── unit/
│   ├── test_rebalance_core.py     # Algorithm unit tests
│   ├── test_rebalance_service.py  # Orchestration + fee logic
│   ├── test_cache.py              # LocalCache + RedisCache
│   └── test_schema_validation.py  # Pydantic model validation
└── integration/
    └── test_rebalance_endpoint.py # End-to-end HTTP tests
```

## Running the Server

```bash
uvicorn app.main:app --reload
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

| Variable             | Default                       | Description                                                          |
|----------------------|-------------------------------|----------------------------------------------------------------------|
| `LOG_LEVEL`          | `INFO`                        | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)           |
| `CACHE_BACKEND`      | `local`                       | `local`: in-memory per process; `redis`: shared across workers       |
| `CACHE_TTL_SECONDS`  | `300`                         | Price cache TTL in seconds (5 minutes)                               |
| `REDIS_URL`          | `redis://localhost:6379/0`    | Redis connection URL (used only when `CACHE_BACKEND=redis`)          |
| `CORS_ORIGINS`       | *(unset)*                     | Comma-separated allowed origins. Only needed when frontend and backend are on different origins. |

## Running Tests

```bash
python -m unittest discover -v
```

## API Reference

### `POST /v1/rebalance`

**Request body** (`application/json`):

```json
{
    "only_buy": true,
    "increment": 1000,
    "optimal_redistribute": false,
    "assets": [
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

| Field                         | Type    | Description                                                                          |
|-------------------------------|---------|--------------------------------------------------------------------------------------|
| `only_buy`                    | bool    | If `true`, never sell; redistribute increment among underweight assets only          |
| `increment`                   | float   | Cash to invest this period (e.g. monthly savings)                                    |
| `optimal_redistribute`        | bool    | *(optional, default `false`)* Use the exact knapsack DP for the leftover-change step |
| `assets[].ticker`             | string  | Yahoo Finance ticker symbol (non-empty)                                              |
| `assets[].desired_percentage` | float   | Target allocation weight; all assets must sum to **100**                             |
| `assets[].shares`             | float   | Shares currently held (>= 0)                                                         |
| `assets[].percentage_fee`     | bool    | *(optional, default `false`)* `false`: flat fee; `true`: % of rebalance allocation  |
| `assets[].fees`               | float   | Broker fee: absolute amount when `percentage_fee` is `false`, or 0-100 when `true`  |

**Response** (`200 OK`):

```json
{
    "results": [
        {
            "id": 0,
            "ticker": "VWCE.DE",
            "current_percentage": 37.45,
            "desired_percentage": 60.0,
            "shares": 10,
            "allocated": 594.05,
            "ticker_price": 118.42,
            "fees": 2.97,
            "buy": 5
        },
        {
            "id": 1,
            "ticker": "VAGF.DE",
            "current_percentage": 62.55,
            "desired_percentage": 40.0,
            "shares": 5,
            "allocated": 398.5,
            "ticker_price": 23.18,
            "fees": 1.5,
            "buy": 17
        }
    ],
    "total_fees": 4.47,
    "change": 6.52
}
```

## Calling the API

### curl

```bash
curl -X POST http://localhost:8000/v1/rebalance \
     -H "Content-Type: application/json" \
     -d '{
       "only_buy": true,
       "increment": 1000,
       "assets": [
         {"ticker": "VWCE.DE", "desired_percentage": 60, "shares": 10, "fees": 0.5, "percentage_fee": true},
         {"ticker": "VAGF.DE", "desired_percentage": 40, "shares": 5,  "fees": 1.5, "percentage_fee": false}
       ]
     }'
```

From a portfolio file:

```bash
curl -X POST http://localhost:8000/v1/rebalance \
     -H "Content-Type: application/json" \
     -d @portfolios/portfolio.json | jq
```

### Python (`httpx`)

```python
import httpx

payload = {
    "only_buy": True,
    "increment": 1000,
    "optimal_redistribute": False,
    "assets": [
        {"ticker": "VWCE.DE", "desired_percentage": 60, "shares": 10, "fees": 0.5, "percentage_fee": True},
        {"ticker": "VAGF.DE", "desired_percentage": 40, "shares": 5,  "fees": 1.5, "percentage_fee": False},
    ],
}

response = httpx.post("http://localhost:8000/v1/rebalance", json=payload)
response.raise_for_status()
print(response.json())
```

### PowerShell

```powershell
$body = @{
    only_buy  = $true
    increment = 1000
    assets    = @(
        @{ ticker = "VWCE.DE"; desired_percentage = 60; shares = 10; fees = 0.5;  percentage_fee = $true  }
        @{ ticker = "VAGF.DE"; desired_percentage = 40; shares = 5;  fees = 1.50; percentage_fee = $false }
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/rebalance `
    -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 5
```

## Fee Types

| percentage_fee   | fees meaning          | Example                          |
|------------------|-----------------------|----------------------------------|
| `false`          | Flat amount per trade | `"fees": 1.50` -> 1.50 deducted  |
| `true`           | % of rebalance amount | `"fees": 0.5` -> 0.5% deducted   |

```
effective_fee  = rebalance_allocation * fees / 100
net_investable = rebalance_allocation - effective_fee
```

The `fees` field in the response always shows the effective absolute fee paid.

## The `optimal_redistribute` Flag

| Algorithm                        | Trade-off                                                                                                   |
|----------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Greedy** (default)             | O(n log n); fast but can leave cash unspent if share prices do not evenly divide the leftover               |
| **Optimal knapsack DP** (opt-in) | O(n * c) in integer cents; maximises cash spent with a tiebreaker that prefers the most underweight assets  |

The greedy algorithm is also used as a fallback when `change_cents > 1,000,000` (~10,000), regardless of flag, to bound memory and time.

When `only_buy=true` the DP additionally excludes already-overweight assets during redistribution; the buy-only constraint is preserved even for leftover change.

### `GET /v1/tickers/search`

Search for instruments by ticker symbol or name. Covers equities, ETFs, mutual funds, cryptocurrencies, and currency pairs. Indices, futures, and options are excluded.

**Query parameters:**

| Parameter | Required | Description                        |
|-----------|----------|------------------------------------|
| `q`       | yes      | Search query, minimum 2 characters |

**Response** (`200 OK`):

```json
{
    "results": [
        {
            "ticker": "VWCE.DE",
            "name": "Vanguard FTSE All-World UCITS ETF",
            "exchange": "XETRA",
            "type": "ETF"
        }
    ]
}
```

Returns `422` when `q` is absent or shorter than 2 characters. Returns `503` when Yahoo Finance is unreachable.
