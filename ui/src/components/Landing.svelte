<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let collapsed: boolean;
  const dispatch = createEventDispatcher<{ toggleCollapsed: void }>();
</script>

<section>
  <details open={!collapsed} on:toggle={e => {
    const open = (e.target as HTMLDetailsElement).open;
    if (open === collapsed) dispatch('toggleCollapsed');
  }}>
    <summary class="section-title" style="cursor: pointer; list-style: none; user-select: none; width: fit-content;">
      About this tool
    </summary>

    <div class="card landing-card">
      <p class="body">
        Most passive investors already know the theory: low-cost ETFs, diversification,
        recurring buys, and rebalancing. What often breaks is execution. Spreadsheets
        become fragile, manual calculations drift, and allocation choices end up inconsistent.
      </p>
      <p class="body">
        DCA OPT is the open source operating layer for investors who have already chosen
        their strategy and want to apply it with rigor. Set your target weights, enter your
        current holdings, add the cash you want to invest, and the tool calculates how many
        shares to buy to move your portfolio as close as possible to the target.
      </p>
      <p class="body">
        It is not a financial advisor, a trading app, or a black box. Every result is
        deterministic, explainable, and verifiable. The logic is readable, the formulas
        are documented, and the full stack is open, self-hostable, and contribution-friendly.
      </p>
      <p class="tagline">Built for passive investors who want clarity, not magic.</p>
    </div>
  </details>
</section>

<style>
  .landing-card {
    margin-top: 16px;
    padding: 20px 24px;
  }

  .body {
    font-size: 0.875rem;
    color: var(--text);
    line-height: 1.7;
    margin: 0 0 10px;
    text-align: justify;
    text-align-last: left;
    text-wrap: pretty;
    hyphens: auto;
  }

  .tagline {
    font-size: 0.875rem;
    color: var(--text-3);
    line-height: 1.6;
    margin: 0;
    text-align: justify;
    text-align-last: left;
    text-wrap: pretty;
  }
</style>
