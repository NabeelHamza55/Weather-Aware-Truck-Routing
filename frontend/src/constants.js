// Risk levels, in increasing severity. `heat` is the 0..1 intensity used by the heatmap.
// Low is 0 on purpose: the heat layer adds overlapping points together, so a calm
// corridor would otherwise look risky. No heat means no meaningful weather risk.
export const LEVELS = {
  low: { label: 'Low', color: '#2e9e5b', heat: 0 },
  moderate: { label: 'Moderate', color: '#e5c100', heat: 0.4 },
  high: { label: 'High', color: '#f08a24', heat: 0.65 },
  severe: { label: 'Severe', color: '#d62f2f', heat: 0.9 },
  no_travel: { label: 'No Travel', color: '#5b1a6b', heat: 1 },
}

// Same order as the backend's numeric levels (0..4).
export const LEVEL_ORDER = ['low', 'moderate', 'high', 'severe', 'no_travel']

export const ROUTE_COLORS = ['#1f6feb', '#8250df', '#0a7f8c']

export const INTERVALS = [10, 25, 50]
