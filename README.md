# DCA OPT

Most passive investors already know the theory: low-cost ETFs, diversification,
recurring buys, and rebalancing. What often breaks is execution. Spreadsheets
become fragile, manual calculations drift, and allocation choices end up inconsistent.

DCA OPT is the open source operating layer for investors who have already chosen
their strategy and want to apply it with rigor. Set your target weights, enter your
current holdings, add the cash you want to invest, and the tool calculates how many
shares to buy to move your portfolio as close as possible to the target.

It is not a financial advisor, a trading app, or a black box. Every result is
deterministic, explainable, and verifiable. The logic is readable, the formulas
are documented, and the full stack is open, self-hostable, and contribution-friendly.

*Built for passive investors who want clarity, not magic.*

## Prerequisites

- Python 3.11+
- Node.js 20+

## Quick Start

### Backend

```bash
python -m venv venv

# Windows
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

### Frontend

```bash
cd ui && npm install
npm run dev
```

UI available at `http://localhost:5173`.

Run both concurrently. In dev mode, Vite proxies `/v1/*` to the backend automatically.

For backend details (API reference, configuration, tests) see [`app/README.md`](app/README.md).

For frontend details (structure, build) see [`ui/README.md`](ui/README.md).
