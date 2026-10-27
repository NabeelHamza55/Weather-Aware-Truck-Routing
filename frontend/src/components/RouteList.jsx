import { LEVELS, LEVEL_ORDER, ROUTE_COLORS } from '../constants'
import { formatDuration, formatTime } from '../format'

// A thin bar split into coloured parts: one part per risk level, sized by miles.
function RiskBar({ miles }) {
  let total = 0
  for (const level of LEVEL_ORDER) {
    total += miles[level]
  }

  return (
    <div className="riskbar">
      {LEVEL_ORDER.map((level) => {
        if (miles[level] === 0) {
          return null
        }
        const width = (miles[level] / total) * 100 + '%'
        return (
          <span
            key={level}
            style={{ width: width, background: LEVELS[level].color }}
            title={LEVELS[level].label + ': ' + miles[level] + ' mi'}
          />
        )
      })}
    </div>
  )
}

// One card per route. Click a card to select that route on the map.
export default function RouteList({ routes, recommendedId, selectedId, onSelect }) {
  // Best route first.
  const sortedRoutes = routes.slice().sort((a, b) => a.rank - b.rank)

  return (
    <ul className="routes">
      {sortedRoutes.map((route) => {
        const summary = route.summary
        const miles = summary.miles_by_level
        const lastCheckpoint = route.checkpoints[route.checkpoints.length - 1]

        return (
          <li key={route.id} className={route.id === selectedId ? 'selected' : ''}>
            <button type="button" onClick={() => onSelect(route.id)}>
              <div className="route-head">
                <span className="swatch" style={{ background: ROUTE_COLORS[route.id] }} />
                <strong>{route.name}</strong>
                {route.id === recommendedId && <span className="badge good">Recommended</span>}
                {!route.driveable && <span className="badge bad">No Travel</span>}
                <span className="worst" style={{ color: LEVELS[summary.worst_level].color }}>
                  Worst: {LEVELS[summary.worst_level].label}
                </span>
              </div>
              <div className="route-stats">
                <span>{summary.distance_miles} mi</span>
                <span>{formatDuration(summary.duration_minutes)}</span>
                <span>Arrive {formatTime(lastCheckpoint.eta)}</span>
              </div>
              <RiskBar miles={miles} />
              <div className="route-risk">
                <span>Severe {miles.severe} mi</span>
                <span>High {miles.high} mi</span>
                <span title="0 = all Low, 4 = all No Travel">Avg risk {summary.avg_risk} / 4</span>
              </div>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
