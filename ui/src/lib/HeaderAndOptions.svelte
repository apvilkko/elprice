<script lang="ts">
  import { LANGUAGES, currentLanguage, isValidLanguage } from "./i18n"
  import { setParam } from "./param"
  import type { Language } from "./types"

  const changeLanguage = (lang: Language) => {
    if (isValidLanguage(lang)) {
      currentLanguage.set(lang)
      setParam("lang", lang)
    }
  }
</script>

<ul>
  {#each LANGUAGES as lang}
    <li>
      {#if $currentLanguage === lang}
        {lang}
      {:else}
        <button type="button" on:click={() => changeLanguage(lang)}
          >{lang}</button
        >
      {/if}
    </li>
  {/each}
</ul>
