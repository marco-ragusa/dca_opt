<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    requestImport: void;
    requestExport: void;
  }>();
</script>

<header>
  <div class="max-w-4xl mx-auto px-5">
    <span class="brand">DCA OPT</span>
    <div style="flex: 1;"></div>
    <div style="display: flex; gap: 6px; flex-shrink: 0;">
      <button type="button" class="btn btn-ghost" on:click={() => dispatch('requestImport')}>Import</button>
      <button type="button" class="btn btn-ghost" on:click={() => dispatch('requestExport')}>Export</button>
    </div>
  </div>
</header>

<style>
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  header > div {
    height: 52px;
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .brand {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text);
    flex-shrink: 0;
  }
</style>
