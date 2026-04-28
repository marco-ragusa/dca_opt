<script lang="ts">
  export let sum: number;

  $: valid = Math.abs(sum - 100) <= 0.01;
  $: display = sum.toFixed(2);
</script>

<div style="display: flex; align-items: center; gap: 8px;">
  <div style="
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {valid ? 'var(--accent)' : 'var(--error)'};
    flex-shrink: 0;
    transition: background 120ms;
  "></div>
  <span style="
    font-family: var(--ff-mono);
    font-size: 0.75rem;
    color: {valid ? 'var(--text-3)' : 'var(--error)'};
    transition: color 120ms;
  ">
    {display}% total{valid ? '' : ' — must equal 100%'}
  </span>
</div>
