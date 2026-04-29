<!-- ui/src/components/TickerAutocomplete.svelte -->
<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';

  export let value: string = '';
  export let id: string = '';

  interface TickerResult {
    ticker: string;
    name: string;
    exchange: string;
    type: string;
  }

  const dispatch = createEventDispatcher<{ change: string }>();

  let results: TickerResult[] = [];
  let open = false;
  let debounceTimer: ReturnType<typeof setTimeout>;

  function onInput(e: Event) {
    const q = (e.target as HTMLInputElement).value.trim().toUpperCase();
    value = q;
    dispatch('change', q);

    clearTimeout(debounceTimer);
    results = [];
    open = false;

    if (q.length < 2) return;

    debounceTimer = setTimeout(() => fetchResults(q), 300);
  }

  async function fetchResults(q: string) {
    try {
      const res = await fetch(`/v1/tickers/search?q=${encodeURIComponent(q)}`);
      if (!res.ok) return;
      const data = await res.json();
      results = data.results ?? [];
      open = true;
    } catch {
      // network error — field remains manually editable
    }
  }

  function select(ticker: string) {
    value = ticker;
    dispatch('change', ticker);
    open = false;
    results = [];
  }

  function onBlur() {
    setTimeout(() => { open = false; }, 150);
  }

  onDestroy(() => clearTimeout(debounceTimer));
</script>

<div class="autocomplete-wrapper">
  <input
    {id}
    type="text"
    {value}
    placeholder="VWCE.DE"
    on:input={onInput}
    on:blur={onBlur}
    class="field mono"
    style="text-transform: uppercase;"
    autocomplete="off"
    spellcheck="false"
  />
  {#if open}
    <ul class="autocomplete-dropdown" role="listbox">
      {#each results as result (result.ticker)}
        <li
          role="option"
          aria-selected="false"
          on:mousedown|preventDefault={() => select(result.ticker)}
          class="autocomplete-item"
        >
          <span class="autocomplete-ticker">{result.ticker}</span>
          <span class="autocomplete-name">{result.name}</span>
        </li>
      {/each}
      {#if results.length === 0}
        <li class="autocomplete-empty">No results</li>
      {/if}
    </ul>
  {/if}
</div>

<style>
  .autocomplete-wrapper {
    position: relative;
    width: 100%;
  }

  .autocomplete-dropdown {
    position: absolute;
    top: calc(100% + 2px);
    left: 0;
    right: 0;
    z-index: 10;
    list-style: none;
    margin: 0;
    padding: 2px 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    max-height: 220px;
    overflow-y: auto;
  }

  .autocomplete-item {
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 6px 10px;
    cursor: pointer;
  }

  .autocomplete-item:hover {
    background: var(--bg);
  }

  .autocomplete-ticker {
    font-family: var(--ff-mono);
    font-size: 0.8125rem;
    color: var(--text);
    white-space: nowrap;
  }

  .autocomplete-name {
    font-size: 0.75rem;
    color: var(--text-2);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .autocomplete-empty {
    padding: 6px 10px;
    font-size: 0.8125rem;
    color: var(--text-3);
  }
</style>
