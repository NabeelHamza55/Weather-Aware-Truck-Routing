import { LEVELS, LEVEL_ORDER } from '../constants'

function hourLabel(startIso, hour) {
  const when = new Date(new Date(startIso).getTime() + hour * 3600 * 1000)
  const clock = when.toLocaleString([], { weekday: 'short', hour: 'numeric' })
  return hour === 0 ? `Now (${clock})` : `+${hour} h · ${clock}`
}

export default function HeatmapControl({ heatmap, hour, onHour, show, onShow }) {
  return (
    <div className="heat-control">
      <div className="heat-head">
        <strong>Weather forecast</strong>
        <label className="toggle">
          <input type="checkbox" checked={show} onChange={(e) => onShow(e.target.checked)} /> Heatmap
        </label>
      </div>
      <input
        type="range"
        min="0"
        max={heatmap.hours - 1}
        value={hour}
        disabled={!show}
        onChange={(e) => onHour(Number(e.target.value))}
        aria-label="Forecast hour"
      />
      <div className="heat-label">{hourLabel(heatmap.start, hour)}</div>
      <div className="legend">
        {LEVEL_ORDER.map((k) => (
          <span key={k}>
            <i style={{ background: LEVELS[k].color }} /> {LEVELS[k].label}
          </span>
        ))}
      </div>
    </div>
  )
}
