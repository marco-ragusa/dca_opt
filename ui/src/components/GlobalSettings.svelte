<script lang="ts">
  import type { Settings } from '../types';
  import { createEventDispatcher } from 'svelte';

  export let increment: number;
  export let onlyBuy: boolean;
  export let optimalRedistribute: boolean;

  const dispatch = createEventDispatcher<{ update: Partial<Settings> }>();
</script>

<div class="card" style="padding: 20px 24px;">
  <p class="section-title" style="margin: 0 0 16px;">Session settings</p>

  <div style="display: grid; grid-template-columns: 1fr; gap: 16px;" class="sm:grid-cols-3">
    <div>
      <label class="lbl" for="increment">Cash to deploy</label>
      <input
        id="increment"
        type="number"
        min="0"
        step="any"
        value={increment}
        on:input={e => dispatch('update', { increment: parseFloat((e.target as HTMLInputElement).value) || 0 })}
        class="field mono"
      />
      <p style="font-size: 0.6875rem; color: var(--text-3); margin: 4px 0 0; line-height: 1.4;">
        Amount to invest this period. Use 0 to rebalance without adding cash.
      </p>
    </div>

    <div>
      <p class="lbl" style="margin-bottom: 12px;">Only buy</p>
      <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
        <input
          type="checkbox"
          checked={onlyBuy}
          on:change={e => dispatch('update', { onlyBuy: (e.target as HTMLInputElement).checked })}
        />
        <span style="font-size: 0.8125rem; color: var(--text-2);">Never sell existing positions</span>
      </label>
    </div>

    <div>
      <p class="lbl" style="margin-bottom: 12px;">Optimal redistribute</p>
      <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
        <input
          type="checkbox"
          checked={optimalRedistribute}
          on:change={e => dispatch('update', { optimalRedistribute: (e.target as HTMLInputElement).checked })}
        />
        <span style="font-size: 0.8125rem; color: var(--text-2);">Use Knapsack algorithm to minimise leftover cash</span>
      </label>
    </div>
  </div>
</div>
