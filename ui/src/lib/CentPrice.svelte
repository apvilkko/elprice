<script lang="ts">
  export let value: number | undefined
</script>

{#if typeof value !== "undefined"}
  <span>{(value * 100).toFixed(2).replace(".", ",")}</span>
{/if}
