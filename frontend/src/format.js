export function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h ? `${h} h ${m} min` : `${m} min`
}

export function formatTime(iso) {
  return new Date(iso).toLocaleString([], {
    weekday: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}

// Value for <input type="datetime-local">, in the browser's local time.
export function toLocalInputValue(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
