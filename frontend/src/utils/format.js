export function formatAmount(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '—'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(numeric)
}

export function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

export function shortId(value) {
  return value ? `${value.slice(0, 8)}…${value.slice(-4)}` : '—'
}
