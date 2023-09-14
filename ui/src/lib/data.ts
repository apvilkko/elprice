import { writable } from "svelte/store"
import type { PriceData, RGB } from "./types"
import { getParam } from "./param"

export const lastModified = writable<Date>()

export const prices = writable<PriceData[]>([])

const toNumber = (v: string | null | undefined) =>
  v === null ? NaN : Number(String(v).replace(",", "."))

const isGoodTax = (val: number) => !Number.isNaN(val) && val >= 0 && val < 99
const isGoodMargin = isGoodTax
const isGoodLimit = isGoodTax

export const tax = writable<number>(
  getParam<number>("tax", isGoodTax, toNumber, 24)
)

export const margin = writable<number>(
  getParam<number>("m", isGoodMargin, toNumber, 0)
)

export const colors = writable<[RGB, RGB, RGB]>([
  [18, 97, 96],
  [77, 62, 64],
  [93, 14, 34],
])

export const timeSpans = writable<[number, number]>([3, 6])

const LIMIT_DEFAULTS = [0.01, 0.1]

const getInitialLimits = () => {
  const low = getParam<number>(
    "cl",
    isGoodLimit,
    toNumber,
    LIMIT_DEFAULTS[0]
  ) as number
  const high = getParam<number>(
    "el",
    isGoodLimit,
    toNumber,
    LIMIT_DEFAULTS[1]
  ) as number
  if (low < high) {
    return [low, high]
  }
  return LIMIT_DEFAULTS
}

export const limits = writable(getInitialLimits())

const DUMMY = import.meta.env.MODE === "development"

export const readStaticData = async () => {
  let jsonData
  if (DUMMY) {
    const dummy = await import("../../../dummy.json")
    jsonData = { data: dummy.default, updated: new Date().toISOString() }
    console.log("using dummy", jsonData)
  } else {
    const attr =
      document.getElementsByTagName("body")[0].getAttribute("data-prices") ??
      "{}"
    jsonData = JSON.parse(attr)
  }
  lastModified.set(new Date(jsonData.updated))
  prices.set(jsonData.data ?? [])
}
