import { get, writable } from "svelte/store"
import type { Language } from "./types"
import { getParam } from "./param"

export const LANGUAGES = ["fi", "en"]

export const isValidLanguage = (lang: Language) => LANGUAGES.includes(lang)

const DEFAULT_LANG = getParam("lang", isValidLanguage) ?? LANGUAGES[0]

export const currentLanguage = writable<Language>(DEFAULT_LANG)

const TRANSLATIONS: Array<Record<Language, string>> = [
  {
    fi: "Sähkön hinta",
    en: "Electricity price",
  },
  {
    fi: "Klo",
    en: "Time",
  },
  {
    fi: "Huomenna",
    en: "Tomorrow",
  },
  {
    fi: "Tänään",
    en: "Today",
  },
  {
    fi: "Hinnat haettu",
    en: "Prices updated",
  },
  {
    fi: "PK",
    en: "WM",
  },
  {
    fi: "Hinnat sis. veron",
    en: "Prices incl. tax",
  },
  {
    fi: "marginaali",
    en: "margin",
  },
]

const TRANS_MAP = TRANSLATIONS.reduce((acc, curr) => {
  acc[curr["fi"]] = curr
  return acc
}, {} as Record<string, Record<Language, string>>)

let subscribed = false
let currLang = get(currentLanguage)

export const t = (key: string) => {
  if (!subscribed) {
    currentLanguage.subscribe((lang) => {
      currLang = lang
    })
  }

  const missing = `MISSING TRANSLATION: ${key}`
  const obj = TRANS_MAP[key]
  if (!obj) {
    return missing
  }
  return obj[currLang] ?? missing
}
