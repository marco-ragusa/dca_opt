<script lang="ts">
  import type { RebalanceResponse } from '../types';
  import AssetResult from './AssetResult.svelte';

  export let result: RebalanceResponse | null;

  let copied = false;

  function copyJson() {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    copied = true;
    setTimeout(() => { copied = false; }, 1800);
  }
</script>

{#if result}
  <section id="results" style="display: flex; flex-direction: column; gap: 20px;">

    <div style="display: flex; align-items: center; gap: 12px;">
      <p class="section-title" style="margin: 0;">Results</p>
      <hr class="divider" style="flex: 1;" />
      <button type="button" class="btn btn-ghost" on:click={copyJson}>
        {copied ? 'Copied' : 'Copy JSON'}
      </button>
    </div>

    <div style="display: flex; flex-direction: column; gap: 8px;">
      {#each result.results as asset (asset.id)}
        <AssetResult {asset} />
      {/each}
    </div>

    <div class="card" style="padding: 16px 20px; display: flex; flex-wrap: wrap; gap: 32px; align-items: center;">
      <div>
        <p class="section-title" style="margin: 0 0 4px;">Total fees</p>
        <span style="font-family: var(--ff-mono); font-size: 1.0625rem; font-weight: 500; color: var(--text); font-variant-numeric: tabular-nums;">
          {result.total_fees.toFixed(2)}
        </span>
      </div>
      <div>
        <p class="section-title" style="margin: 0 0 4px;">Leftover cash</p>
        <span style="font-family: var(--ff-mono); font-size: 1.0625rem; font-weight: 500; color: var(--text); font-variant-numeric: tabular-nums;">
          {result.change.toFixed(2)}
        </span>
      </div>
      <div style="margin-left: auto;">
        <p class="section-title" style="margin: 0 0 4px;">Assets</p>
        <span style="font-family: var(--ff-mono); font-size: 1.0625rem; font-weight: 500; color: var(--text);">
          {result.results.length}
        </span>
      </div>
    </div>
  </section>
{/if}
