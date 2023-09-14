export type Language = string

export type PriceData = {
  DateTime: string
  PriceNoTax: number
}

export type PriceItem = {
  hour: number
  price: number
}

export type RGB = [number, number, number]

export type Stats = {
  max: PriceItem
  min: PriceItem
  pkMax: PriceItem
  pkMin: PriceItem
  average: number
  shortBest: number[]
  longBest: number[]
}
