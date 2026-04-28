# Frontend

Svelte + TypeScript single-page application. Communicates with the backend via
a single endpoint (`POST /v1/rebalance`).

## Structure

```
ui/
├── src/
│   ├── main.ts                        # App mount point
│   ├── App.svelte                     # Root component (state, rebalance call, dark mode)
│   ├── app.css                        # Global styles
│   ├── types.ts                       # TypeScript interfaces (Asset, Settings, API shapes)
│   ├── storage.ts                     # localStorage persistence helpers
│   └── components/
│       ├── Header.svelte              # Top bar (logo, import/export, dark mode toggle)
│       ├── Landing.svelte             # Collapsible info/welcome section
│       ├── GlobalSettings.svelte      # Increment, only-buy, optimal-redistribute controls
│       ├── PortfolioEditor.svelte     # Asset table + settings form + run button
│       ├── AssetRow.svelte            # Single asset editor row
│       ├── ResultsPanel.svelte        # Results view (shown after a successful run)
│       ├── AssetResult.svelte         # Single result row (buy qty, fees, allocations)
│       ├── PercentageIndicator.svelte # Visual bar: current vs desired allocation
│       └── ErrorMessage.svelte        # Error toast/alert
├── public/
│   ├── favicon.svg
│   └── icons.svg                      # SVG icon sprite
├── index.html                         # Entry point (dark mode init script, mounts #app)
├── vite.config.ts                     # Dev proxy: /v1/* to localhost:8000
├── svelte.config.js
├── tailwind.config.js
├── postcss.config.js
└── tsconfig.json
```

## Development

```bash
npm install
npm run dev
```

UI available at `http://localhost:5173`.

Vite proxies all `/v1/*` requests to `http://localhost:8000` in dev mode, so no
CORS configuration is needed. The backend must be running concurrently.

## Production Build

```bash
npm run build
# Output: dist/
```

The bundle can be served by any static file server. If the frontend and backend
are deployed on different origins, set `CORS_ORIGINS` in the backend `.env`.
