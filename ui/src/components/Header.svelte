<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let exportDisabled = false;
  export let dark = false;

  const dispatch = createEventDispatcher<{
    requestImport: void;
    requestExport: void;
    toggleDark: void;
  }>();
</script>

<header>
  <div class="max-w-4xl mx-auto px-5">
    <span class="brand">DCA OPT</span>
    <div style="flex: 1;"></div>
    <div style="display: flex; gap: 6px; flex-shrink: 0; align-items: center;">
      <button
        type="button"
        class="btn btn-ghost btn-icon"
        on:click={() => dispatch('toggleDark')}
        aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {#if dark}
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4"/>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
          </svg>
        {/if}
      </button>
      <button type="button" class="btn btn-ghost" on:click={() => dispatch('requestImport')}>Import</button>
      <button type="button" class="btn btn-ghost" on:click={() => dispatch('requestExport')} disabled={exportDisabled}>Export</button>
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
