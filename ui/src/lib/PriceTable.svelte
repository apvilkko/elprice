<script lang="ts">
  import type { StartStopNotifier } from "svelte/store"
  import CentPrice from "./CentPrice.svelte"
  import { colors, lastModified, limits, margin, prices, tax } from "./data"
  import { currentLanguage, t } from "./i18n"
  import type { PriceItem, Stats } from "./types"

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
  let stats: [Stats, Stats] = [{} as Stats, {} as Stats]

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
      const beforeTax = row.PriceNoTax + $margin / 100.0
      const price = beforeTax < 0 ? beforeTax : beforeTax * (1.0 + $tax / 100.0)
      const item = { hour, price }
      if (dayMatches(time, today)) {
        perDay[0][hour] = item
      } else if (dayMatches(time, tomorrow)) {
        perDay[1][hour] = item
      }
    }

    const allPrices: PriceItem[] = [
      ...perDay[0],
      ...perDay[1].map((x) => ({ ...x, hour: x.hour + 24 })),
    ]
    ;[0, 1].forEach((dayOffset) => {
      const nonNullPrices = allPrices
        .slice(dayOffset * 24, (1 + dayOffset) * 24)
        .filter((x) => typeof x.price !== "undefined")

      let max = { price: -1e6, hour: -1 }
      let min = { price: 1e6, hour: -1 }
      nonNullPrices.forEach((item) => {
        if (item.price > max.price) {
          max = item
        }
        if (item.price < min.price) {
          min = item
        }
      })

      stats[dayOffset].max = max
      stats[dayOffset].min = min
      stats[dayOffset].average =
        nonNullPrices.reduce((a, b) => a + b.price, 0) / nonNullPrices.length
    })
  }

  const h = (x: number) => {
    return x.toString(16).padStart(2, "0")
  }

  const rgb2hex = (c: [number, number, number] | undefined) => {
    if (typeof c === "undefined") return ""
    console.log("rgb2hex", c, `${h(c[0])}${h(c[1])}${h(c[2])}`)
    return `#${h(c[0])}${h(c[1])}${h(c[2])}`
  }

  const linInterp = (
    a: number,
    c1: number[],
    c2: number[]
  ): [number, number, number] => {
    const c = 1.0 - a
    return [
      Math.round(c2[0] * a + c1[0] * c),
      Math.round(c2[1] * a + c1[1] * c),
      Math.round(c2[2] * a + c1[2] * c),
    ]
  }

  const colorForPrice = (
    priceEur: number
  ): [number, number, number] | undefined => {
    const lastLimit = $limits[$limits.length - 1]
    if (typeof priceEur === "undefined") return undefined
    if (priceEur <= $limits[0]) return $colors[0]
    else if (priceEur >= lastLimit) return $colors[$colors.length - 1]
    const pos = priceEur / (lastLimit - $limits[0])
    if (pos < 0.5) return linInterp(pos * 2.0, $colors[0], $colors[1])
    else return linInterp((pos - 0.5) * 2.0, $colors[1], $colors[2])
  }

  const getCellStyle = (day: number, index: number) => {
    const price = perDay[day][index].price
    const max = stats[day].max.price
    const min = stats[day].min.price
    const percent = ((price - min) / (max - min)) * 100
    const invPercent = 100 - percent
    const color = rgb2hex(colorForPrice(price))
    const common = ""
    if (percent === 100 || typeof color === "undefined") {
      return `background-color: ${color};${common}`
    } else {
      return `background: linear-gradient(to right, ${color} 0% ${percent}%, rgba(0,0,0,0) ${percent}% ${invPercent}%);${common}`
    }
  }
</script>

<p>
  {t("Hinnat haettu")}
  {$lastModified?.toLocaleString("fi")}. {t("Hinnat sis. veron")}
  {$tax}%, {t("marginaali")}
  {String($margin).replace(".", ",")}
  {t("snt")}/kWh.
</p>
<table>
  <thead>
    <tr>
      <th style="width: 2em;" class="time">{t("Klo")}</th><th
        >{t("Tänään")} {shortDate(today)}</th
      ><th style="width: 3em;">{t("PK")}</th><th
        >{t("Huomenna")} {shortDate(tomorrow)}</th
      ><th style="width: 3em;">{t("PK")}</th>
    </tr>
  </thead>
  <tbody>
    {#each perDay[0] as todayData, i}
      <tr>
        <td>{todayData.hour}</td>
        <td style={getCellStyle(0, i)}><CentPrice value={todayData.price} /></td
        >
        <td />
        <td style={getCellStyle(1, i)}
          ><CentPrice value={perDay[1][i].price} /></td
        >
        <td />
      </tr>
    {/each}
  </tbody>
</table>
<p>
  {t("Keskihinta")}
  {t("Tänään").toLowerCase()}
  <CentPrice value={stats[0].average} />
  {t("snt")}/kWh; {t("Huomenna").toLowerCase()}
  <CentPrice value={stats[1].average} />
  {t("snt")}/kWh
</p>
