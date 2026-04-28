<script lang="ts">
  export let message: string | null = null;
</script>

{#if message}
  <div style="
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    border-radius: var(--r);
    padding: 12px 16px;
    display: flex;
    align-items: baseline;
    gap: 10px;
  ">
    <span style="font-size: 0.6875rem; font-weight: 600; color: var(--error); flex-shrink: 0;">Error</span>
    <span style="font-size: 0.8125rem; color: var(--error); line-height: 1.5;">{message}</span>
  </div>
{/if}
