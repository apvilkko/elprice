export const getParam = <T = string>(
  key: string,
  validator?: (v: T) => boolean,
  converter?: (v: string) => T,
  defaultValue?: T
) => {
  const def = typeof defaultValue === "undefined" ? undefined : defaultValue
  const params = new URLSearchParams(document.location.search)
  const val = params.get(key) as string
  const value = (converter ? converter(val) : val) as T
  if (validator) {
    return validator(value) ? value : def
  }
  return value ?? def
}

export const setParam = (key: string, value: string) => {
  const params = new URLSearchParams(document.location.search)
  params.set(key, value)
  history.replaceState(undefined, "", `?${params.toString()}`)
}
