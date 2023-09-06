<script lang="ts">
  import CentPrice from "./CentPrice.svelte"
  import { lastModified, margin, prices, tax } from "./data"
  import { currentLanguage, t } from "./i18n"
  import type { PriceItem } from "./types"

  const today = new Date()
  let tomorrow = new Date()
  tomorrow.setDate(today.getDate() + 1)

  const dayMatches = (d1: string, d2: Date) =>
    d1.slice(0, 10) === d2.toISOString().slice(0, 10)

  const shortDate = (date: Date) =>
    `${date.toLocaleString($currentLanguage, {
      weekday: "short",
    })} ${date.getDate()}.${date.getMonth() + 1}.`

  let perDay: [PriceItem[], PriceItem[]]

  $: {
    perDay = [0, 1].map(() =>
      Array.from({ length: 24 }).map((_, i) => ({
        hour: i,
        price: undefined,
      }))
    ) as unknown as [PriceItem[], PriceItem[]]

    for (let i = 0; i < $prices.length; ++i) {
      const row = $prices[i]
      // DateTimes from API are in Finnish TZ, strip this out for
      // compatibility with JS Date
      const time = row.DateTime.slice(0, 19)
      const hour = Number(time.slice(11, 13))
      const price = row.PriceNoTax * (1.0 + $tax / 100.0) + $margin / 100.0
      const item = { hour, price }
      if (dayMatches(time, today)) {
        perDay[0][hour] = item
      } else if (dayMatches(time, tomorrow)) {
        perDay[1][hour] = item
      }
    }
  }

  console.log($margin)
</script>

<p>
  {t("Hinnat haettu")}
  {$lastModified?.toLocaleString("fi")}. {t("Hinnat sis. veron")}
  {$tax}%, {t("marginaali")}
  {$margin} c/kWh.
</p>
<table>
  <thead>
    <tr>
      <th class="time">{t("Klo")}</th><th>{t("Tänään")} {shortDate(today)}</th
      ><th>{t("PK")}</th><th>{t("Huomenna")} {shortDate(tomorrow)}</th><th
        >{t("PK")}</th
      >
    </tr>
  </thead>
  <tbody>
    {#each perDay[0] as todayData, i}
      <tr>
        <td>{todayData.hour}</td>
        <td><CentPrice value={todayData.price} /></td>
        <td />
        <td><CentPrice value={perDay[1][i].price} /></td>
        <td />
      </tr>
    {/each}
  </tbody>
</table>
