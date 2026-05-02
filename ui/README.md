# Frontend

Svelte 4 + TypeScript single-page application. Communicates with the backend via
a single endpoint (`POST /v1/rebalance`) and a ticker search endpoint (`GET /v1/tickers/search`).

## Structure

```
ui/
├── src/
│   ├── main.ts                        # App mount point
│   ├── App.svelte                     # Root component (state, rebalance call, dark mode)
│   ├── app.css                        # Global styles and design tokens
│   ├── types.ts                       # TypeScript interfaces (Asset, Settings, API shapes)
│   ├── storage.ts                     # localStorage persistence helpers
│   └── components/
│       ├── Header.svelte              # Sticky nav (wordmark, import/export, dark mode toggle)
│       ├── Hero.svelte                # Dark hero section with headline and subtitle
│       ├── GlobalSettings.svelte      # Increment, only-buy, optimal-redistribute controls
│       ├── PortfolioEditor.svelte     # Asset table + percentage indicator + run button
│       ├── AssetRow.svelte            # Single asset row (<tr>) inside the asset table
│       ├── TickerAutocomplete.svelte  # Debounced ticker search with keyboard-navigable dropdown
│       ├── PercentageIndicator.svelte # Progress bar: sum of target allocations vs 100%
│       ├── ResultsPanel.svelte        # Full result panel (solver badges, rows, summary, copy JSON)
│       ├── AssetResult.svelte         # Single result row (buy qty, drift bar, allocated)
│       ├── TrustRail.svelte           # Static trust signals strip
│       ├── HowItWorks.svelte          # Static 3-step explainer + API request example
│       ├── AlgoSection.svelte         # Static algorithm modes comparison table
│       └── OssSection.svelte          # Static OSS/self-host section with quickstart
├── public/
│   └── favicon.svg
├── index.html                         # Entry point (Geist fonts, dark mode init script)
├── vite.config.ts                     # Dev proxy: /v1/* → localhost:8000
├── svelte.config.js
├── tailwind.config.js
├── postcss.config.js
└── tsconfig.json
```

## Design system

Global CSS tokens are defined in `app.css` under `:root` and `html.dark`:

- **Teal palette** - `--teal`, `--teal-hover`, `--teal-light`, `--teal-mid`
- **Hero surface** - `--hero-bg`, `--hero-text`, `--hero-sub`, `--hero-border`
- **Typography** - `--sans` (Geist), `--mono` (Geist Mono) via Google Fonts

## Development

```bash
npm install
npm run dev
```

UI available at `http://localhost:5173`.

Vite proxies all `/v1/*` requests to `http://localhost:8000` in dev mode - no
CORS configuration needed. The backend must be running concurrently.

## Production build

```bash
npm run build
# Output: dist/
```

The bundle can be served by any static file server. If the frontend and backend
are deployed on different origins, set `CORS_ORIGINS` in the backend `.env`.
