// Address of the Django server. Empty in development, because vite.config.js
// forwards every /api request to http://localhost:8000.
const BASE_URL = import.meta.env.VITE_API_URL || ''

export async function searchPlaces(query) {
  const response = await fetch(BASE_URL + '/api/geocode?q=' + encodeURIComponent(query))
  if (!response.ok) {
    throw new Error('Search failed')
  }
  return response.json()
}

export async function planRoutes(trip) {
  const response = await fetch(BASE_URL + '/api/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trip),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong')
  }
  return data
}
