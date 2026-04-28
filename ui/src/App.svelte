<script lang="ts">
  import { onMount } from 'svelte';
  import type { Asset, Settings, RebalanceResponse, PortfolioExport } from './types';
  import {
    loadSettings, loadAssets, loadLandingCollapsed,
    saveSettings, saveAssets, saveLandingCollapsed,
    DEFAULT_SETTINGS,
  } from './storage';

  import Header from './components/Header.svelte';
  import Landing from './components/Landing.svelte';
  import PortfolioEditor from './components/PortfolioEditor.svelte';
  import ResultsPanel from './components/ResultsPanel.svelte';
  import ErrorMessage from './components/ErrorMessage.svelte';

  let settings: Settings = DEFAULT_SETTINGS;
  let assets: Asset[] = [];
  let lastResult: RebalanceResponse | null = null;
  let error: string | null = null;
  let loading = false;
  let landingCollapsed = false;

  let fileInput: HTMLInputElement;

  onMount(() => {
    settings = loadSettings();
    assets = loadAssets();
    landingCollapsed = loadLandingCollapsed();
  });

  function updateSettings(patch: Partial<Settings>) {
    settings = { ...settings, ...patch };
    saveSettings(settings);
  }

  function addAsset() {
    const id = crypto.randomUUID();
    assets = [...assets, { id, ticker: '', desiredPercentage: 0, shares: 0, fees: 0, percentageFee: false }];
    saveAssets(assets);
  }

  function removeAsset(id: string) {
    assets = assets.filter(a => a.id !== id);
    saveAssets(assets);
  }

  function updateAsset(id: string, patch: Partial<Asset>) {
    assets = assets.map(a => a.id === id ? { ...a, ...patch } : a);
    saveAssets(assets);
  }

  async function runRebalance() {
    loading = true;
    error = null;
    lastResult = null;

    const body = {
      only_buy: settings.onlyBuy,
      increment: settings.increment,
      optimal_redistribute: settings.optimalRedistribute,
      assets: assets.map(a => ({
        ticker: a.ticker,
        desired_percentage: a.desiredPercentage,
        shares: a.shares,
        fees: a.fees,
        percentage_fee: a.percentageFee,
      })),
    };

    try {
      const res = await fetch('/v1/rebalance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        lastResult = await res.json() as RebalanceResponse;
        setTimeout(() => {
          document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
        }, 50);
      } else if (res.status === 422) {
        const data = await res.json();
        const msgs = Array.isArray(data.detail)
          ? data.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join('; ')
          : String(data.detail);
        error = `Validation error: ${msgs}`;
      } else if (res.status === 502) {
        error = 'Market data unavailable. Check ticker symbols or try again.';
      } else {
        error = 'Request failed. Try again.';
      }
    } catch {
      error = 'Request failed. Is the backend running?';
    } finally {
      loading = false;
    }
  }

  function handleExport() {
    const now = new Date();
    const payload: PortfolioExport = {
      version: 1,
      exportedAt: now.toISOString(),
      settings,
      assets: assets.map(({ id: _id, ...rest }) => rest),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dca-opt-portfolio-${now.toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleImportRequest() {
    fileInput.value = '';
    fileInput.click();
  }

  function handleFileChange(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      const importError = processImport(text);
      if (importError) {
        error = importError;
      }
    };
    reader.readAsText(file);
  }

  function processImport(text: string): string | null {
    let data: unknown;
    try {
      data = JSON.parse(text);
    } catch {
      return 'File is not valid JSON.';
    }

    if (typeof data !== 'object' || data === null) return 'Invalid portfolio file.';
    const d = data as Record<string, unknown>;

    if (d.version !== 1) return 'Unsupported export version. Expected version 1.';
    if (typeof d.settings !== 'object' || d.settings === null) return 'Invalid portfolio file: missing settings.';
    if (!Array.isArray(d.assets) || d.assets.length === 0) return 'Invalid portfolio file: assets must be a non-empty array.';

    const s = d.settings as Record<string, unknown>;
    if (typeof s.increment !== 'number' || s.increment < 0) return 'Invalid portfolio file: invalid increment.';

    for (let i = 0; i < d.assets.length; i++) {
      const a = d.assets[i] as Record<string, unknown>;
      if (typeof a.ticker !== 'string' || !a.ticker) return `Invalid portfolio file: asset ${i + 1} missing ticker.`;
      if (typeof a.desiredPercentage !== 'number' || a.desiredPercentage < 0) return `Invalid portfolio file: asset ${i + 1} invalid desiredPercentage.`;
      if (typeof a.shares !== 'number' || a.shares < 0) return `Invalid portfolio file: asset ${i + 1} invalid shares.`;
      if (typeof a.fees !== 'number' || a.fees < 0) return `Invalid portfolio file: asset ${i + 1} invalid fees.`;
      if (typeof a.percentageFee !== 'boolean') return `Invalid portfolio file: asset ${i + 1} invalid percentageFee.`;
    }

    const sum = (d.assets as Array<{ desiredPercentage: number }>).reduce((s, a) => s + a.desiredPercentage, 0);
    const sumWarning = Math.abs(sum - 100) > 0.01 ? ' (Note: percentages do not sum to 100. Fix before running.)' : '';

    if (!confirm(`This will replace your current portfolio.${sumWarning} Continue?`)) return null;

    const newSettings: Settings = {
      increment: s.increment as number,
      onlyBuy: typeof s.onlyBuy === 'boolean' ? s.onlyBuy : DEFAULT_SETTINGS.onlyBuy,
      optimalRedistribute: typeof s.optimalRedistribute === 'boolean' ? s.optimalRedistribute : DEFAULT_SETTINGS.optimalRedistribute,
    };

    const newAssets: Asset[] = (d.assets as Array<Record<string, unknown>>).map(a => ({
      id: crypto.randomUUID(),
      ticker: a.ticker as string,
      desiredPercentage: a.desiredPercentage as number,
      shares: a.shares as number,
      fees: a.fees as number,
      percentageFee: a.percentageFee as boolean,
    }));

    settings = newSettings;
    assets = newAssets;
    lastResult = null;
    error = null;
    saveSettings(settings);
    saveAssets(assets);
    return null;
  }
</script>

<input
  bind:this={fileInput}
  type="file"
  accept=".json"
  style="display:none"
  on:change={handleFileChange}
  aria-hidden="true"
/>

<Header
  on:requestImport={handleImportRequest}
  on:requestExport={handleExport}
/>

<main style="max-width: 896px; margin: 0 auto; padding: 36px 20px 64px; display: flex; flex-direction: column; gap: 36px;">
  <Landing
    collapsed={landingCollapsed}
    on:toggleCollapsed={() => {
      landingCollapsed = !landingCollapsed;
      saveLandingCollapsed(landingCollapsed);
    }}
  />

  <ErrorMessage message={error} />

  <PortfolioEditor
    {settings}
    {assets}
    {loading}
    on:updateSettings={e => updateSettings(e.detail)}
    on:addAsset={addAsset}
    on:removeAsset={e => removeAsset(e.detail)}
    on:updateAsset={e => updateAsset(e.detail.id, e.detail.patch)}
    on:run={runRebalance}
  />

  <ResultsPanel result={lastResult} />
</main>

<footer style="border-top: 1px solid var(--border); margin-top: auto;">
  <div style="max-width: 896px; margin: 0 auto; padding: 12px 20px; display: flex; align-items: center; gap: 16px;">
    <span style="font-size: 0.75rem; color: var(--text-3);">DCA OPT</span>
    <span style="font-size: 0.6875rem; color: var(--text-3);">v2.0.0</span>
    <a
      href="https://github.com/marco-ragusa/dca_opt"
      target="_blank"
      rel="noopener noreferrer"
      style="font-size: 0.75rem; color: var(--text-3); text-decoration: none; margin-left: auto;"
    >GitHub</a>
  </div>
</footer>
