<script lang="ts">
  import type { Asset, Settings } from '../types';
  import GlobalSettings from './GlobalSettings.svelte';
  import AssetRow from './AssetRow.svelte';
  import PercentageIndicator from './PercentageIndicator.svelte';
  import { createEventDispatcher } from 'svelte';

  export let settings: Settings;
  export let assets: Asset[];
  export let loading: boolean;

  const dispatch = createEventDispatcher<{
    updateSettings: Partial<Settings>;
    addAsset: void;
    removeAsset: string;
    updateAsset: { id: string; patch: Partial<Asset> };
    run: void;
  }>();

  $: percentageSum = assets.reduce((s, a) => s + (a.desiredPercentage || 0), 0);
  $: canRun = Math.abs(percentageSum - 100) <= 0.01 && !loading && assets.length > 0;
</script>

<section style="display: flex; flex-direction: column; gap: 20px;">

  <div style="display: flex; align-items: center; gap: 12px;">
    <p class="section-title" style="margin: 0;">Portfolio</p>
    <hr class="divider" style="flex: 1;" />
  </div>

  <GlobalSettings
    increment={settings.increment}
    onlyBuy={settings.onlyBuy}
    optimalRedistribute={settings.optimalRedistribute}
    on:update={e => dispatch('updateSettings', e.detail)}
  />

  <div style="display: flex; align-items: center; justify-content: space-between;">
    <p class="section-title" style="margin: 0;">Assets</p>
    <button
      type="button"
      class="btn btn-ghost"
      on:click={() => dispatch('addAsset')}
    >
      <span style="font-size: 1rem; line-height: 1; font-weight: 400;">+</span>
      Add asset
    </button>
  </div>

  {#if assets.length === 0}
    <div style="
      padding: 32px 24px;
      text-align: center;
      border: 1px dashed var(--border);
      border-radius: var(--r);
    ">
      <p style="font-size: 0.875rem; color: var(--text-3); margin: 0;">
        No assets yet.
      </p>
    </div>
  {:else}
    <div style="display: flex; flex-direction: column; gap: 8px;">
      {#each assets as asset, i (asset.id)}
        <AssetRow
          {asset}
          index={i}
          on:update={e => dispatch('updateAsset', { id: asset.id, patch: e.detail })}
          on:remove={() => dispatch('removeAsset', asset.id)}
        />
      {/each}
    </div>
  {/if}

  <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding-top: 4px;">
    <PercentageIndicator sum={percentageSum} />

    <button
      type="button"
      class="btn btn-primary"
      on:click={() => dispatch('run')}
      disabled={!canRun}
    >
      {loading ? 'Running…' : 'Run rebalance'}
    </button>
  </div>
</section>
