<script lang="ts">
  import type { Asset } from '../types';
  import { createEventDispatcher } from 'svelte';
  import TickerAutocomplete from './TickerAutocomplete.svelte';

  export let asset: Asset;
  export let index: number;

  const dispatch = createEventDispatcher<{ update: Partial<Asset>; remove: void }>();

  function num(e: Event): number {
    return parseFloat((e.target as HTMLInputElement).value) || 0;
  }
</script>

<div class="card asset-row">
  <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 14px 0;">
    <span style="font-family: var(--ff-mono); font-size: 0.6875rem; color: var(--text-3);">
      {String(index + 1).padStart(2, '0')}
    </span>
    <button
      type="button"
      aria-label="Remove asset"
      on:click={() => dispatch('remove')}
      class="btn btn-danger-text"
    >x</button>
  </div>

  <div class="asset-fields">
    <div class="field-group ticker-group">
      <label class="lbl" for="ticker-{asset.id}">Ticker</label>
      <TickerAutocomplete
        id="ticker-{asset.id}"
        value={asset.ticker}
        on:change={e => dispatch('update', { ticker: e.detail })}
      />
    </div>

    <div class="field-group">
      <label class="lbl" for="pct-{asset.id}">Target %</label>
      <input
        id="pct-{asset.id}"
        type="number"
        min="0"
        max="100"
        step="any"
        value={asset.desiredPercentage}
        on:input={e => dispatch('update', { desiredPercentage: num(e) })}
        class="field mono"
      />
    </div>

    <div class="field-group">
      <label class="lbl" for="shares-{asset.id}">Shares held</label>
      <input
        id="shares-{asset.id}"
        type="number"
        min="0"
        step="any"
        value={asset.shares}
        on:input={e => dispatch('update', { shares: num(e) })}
        class="field mono"
      />
    </div>

    <div class="field-group">
      <label class="lbl" for="fees-{asset.id}">Fees</label>
      <input
        id="fees-{asset.id}"
        type="number"
        min="0"
        step="any"
        value={asset.fees}
        on:input={e => dispatch('update', { fees: num(e) })}
        class="field mono"
      />
    </div>

    <div class="field-group fee-type-group">
      <p class="lbl" style="margin-bottom: 10px;">Fee type</p>
      <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
        <input
          type="checkbox"
          checked={asset.percentageFee}
          on:change={e => dispatch('update', { percentageFee: (e.target as HTMLInputElement).checked })}
        />
        <span style="font-size: 0.8125rem; color: var(--text-2);">Percentage (%)</span>
      </label>
    </div>
  </div>
</div>

<style>
  .asset-row {
    overflow: hidden;
  }

  .asset-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    padding: 8px 14px 14px;
  }

  .ticker-group {
    grid-column: 1 / -1;
  }

  @media (min-width: 640px) {
    .asset-fields {
      grid-template-columns: 1.5fr 1fr 1fr 1fr 1.4fr;
    }
    .ticker-group {
      grid-column: auto;
    }
  }

  .asset-row:focus-within {
    border-color: var(--border-hover);
  }
</style>
