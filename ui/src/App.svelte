<script lang="ts">
  import { onMount } from "svelte"
  import HeaderAndOptions from "./lib/HeaderAndOptions.svelte"
  import PriceTable from "./lib/PriceTable.svelte"
  import { currentLanguage, t } from "./lib/i18n"
  import { readStaticData } from "./lib/data"

  onMount(() => {
    readStaticData()
  })
</script>

{#key $currentLanguage}
  <main>
    <HeaderAndOptions />
    <h1>{t("Sähkön hinta")}</h1>
    <PriceTable />
  </main>
{/key}
