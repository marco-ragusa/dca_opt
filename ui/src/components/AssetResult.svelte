<script lang="ts">
  import type { AssetResultOut } from '../types';

  export let asset: AssetResultOut;

  $: muted = asset.buy === 0;
  $: drift = Math.abs(asset.current_percentage - asset.desired_percentage);
</script>

<div class="card result-card" style="opacity: {muted ? 0.55 : 1};">
  <div class="result-inner">
    <div style="flex: 1; min-width: 0;">
      <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px;">
        <span style="font-family: var(--ff-mono); font-size: 0.9375rem; font-weight: 500; color: var(--text);">
          {asset.ticker}
        </span>
        {#if drift > 0.5}
          <span style="font-size: 0.6875rem; color: var(--text-3);">{drift.toFixed(1)}% drift</span>
        {/if}
      </div>

      <div class="stats-grid">
        <div class="stat-cell">
          <span class="stat-label">Price</span>
          <span class="stat-value">{asset.ticker_price.toFixed(2)}</span>
        </div>
        <div class="stat-cell">
          <span class="stat-label">Allocated</span>
          <span class="stat-value">{asset.allocated.toFixed(2)}</span>
        </div>
        <div class="stat-cell">
          <span class="stat-label">Fees</span>
          <span class="stat-value">{asset.fees.toFixed(2)}</span>
        </div>
        <div class="stat-cell">
          <span class="stat-label">Current</span>
          <span class="stat-value">{asset.current_percentage.toFixed(2)}%</span>
        </div>
        <div class="stat-cell">
          <span class="stat-label">Target</span>
          <span class="stat-value">{asset.desired_percentage.toFixed(2)}%</span>
        </div>
        <div class="stat-cell">
          <span class="stat-label">Held</span>
          <span class="stat-value">{asset.shares}</span>
        </div>
      </div>
    </div>

    <div class="buy-col">
      <span class="buy-count" style="color: {muted ? 'var(--text-3)' : 'var(--accent)'};">{asset.buy}</span>
      <span class="buy-label">share{asset.buy === 1 ? '' : 's'}</span>
    </div>
  </div>
</div>

<style>
  .result-inner {
    display: flex;
    align-items: stretch;
    padding: 14px 18px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px 14px;
  }

  @media (min-width: 640px) {
    .stats-grid {
      grid-template-columns: repeat(6, 1fr);
    }
  }

  .buy-col {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
    flex-shrink: 0;
    padding-left: 18px;
    border-left: 1px solid var(--border);
    min-width: 64px;
    text-align: right;
  }

  .buy-count {
    font-family: var(--ff-mono);
    font-size: 2rem;
    font-weight: 500;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }

  .buy-label {
    font-size: 0.6875rem;
    color: var(--text-3);
    margin-top: 3px;
  }
</style>
