import { useEffect } from 'react'
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, Tooltip, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { LEVELS, ROUTE_COLORS } from '../constants'
import { formatTime } from '../format'
import HeatLayer from './HeatLayer'

// Zooms the map so every route is visible.
function FitToRoutes({ routes }) {
  const map = useMap()

  useEffect(() => {
    if (routes) {
      const allPoints = []
      for (const route of routes) {
        allPoints.push(...route.path)
      }
      map.fitBounds(allPoints, { padding: [40, 40] })
    }
  }, [map, routes])

  return null
}

export default function MapView({ result, selectedId, onSelect, heatHour, showHeat, origin, destination }) {
  const routes = result ? result.routes : []

  // Draw the selected route last so it is on top of the others.
  const drawOrder = routes.slice().sort((a, b) => (a.id === selectedId ? 1 : 0) - (b.id === selectedId ? 1 : 0))

  return (
    <MapContainer center={[39, -98]} zoom={4} preferCanvas className="map">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />

      {result && <FitToRoutes routes={result.routes} />}
      {result && showHeat && <HeatLayer points={result.heatmap.points} hour={heatHour} />}

      {/* The route lines */}
      {drawOrder.map((route) => (
        <Polyline
          key={'line-' + route.id}
          positions={route.path}
          pathOptions={{
            color: ROUTE_COLORS[route.id],
            weight: route.id === selectedId ? 6 : 4,
            opacity: route.id === selectedId ? 0.95 : 0.55,
          }}
          eventHandlers={{ click: () => onSelect(route.id) }}
        />
      ))}

      {/* A coloured dot at every checkpoint. Click one to see the details. */}
      {drawOrder.map((route) =>
        route.checkpoints.map((checkpoint) => (
          <CircleMarker
            key={'checkpoint-' + route.id + '-' + checkpoint.mile}
            center={[checkpoint.lat, checkpoint.lng]}
            radius={route.id === selectedId ? 7 : 4}
            pathOptions={{ color: '#fff', weight: 1.5, fillColor: LEVELS[checkpoint.level].color, fillOpacity: 1 }}
          >
            <Popup>
              <div className="popup">
                <strong>
                  {route.name} · mile {checkpoint.mile}
                </strong>
                <div style={{ color: LEVELS[checkpoint.level].color, fontWeight: 600 }}>
                  {LEVELS[checkpoint.level].label} risk
                </div>
                <div>ETA {formatTime(checkpoint.eta)}</div>
                <div>Wind {checkpoint.wind_mph} mph</div>
                <div>Rain {checkpoint.rain_in_hr} in/hr</div>
                <div>Snow {checkpoint.snow_in_hr} in/hr</div>
                {checkpoint.forecast_out_of_range && (
                  <div className="warn">Beyond forecast range; using the last available data.</div>
                )}
              </div>
            </Popup>
          </CircleMarker>
        )),
      )}

      {/* Start and end of the trip */}
      {origin && (
        <CircleMarker center={[origin.lat, origin.lng]} radius={9} pathOptions={{ color: '#fff', fillColor: '#111', fillOpacity: 1, weight: 2 }}>
          <Tooltip permanent direction="top">Start</Tooltip>
        </CircleMarker>
      )}
      {destination && (
        <CircleMarker center={[destination.lat, destination.lng]} radius={9} pathOptions={{ color: '#fff', fillColor: '#111', fillOpacity: 1, weight: 2 }}>
          <Tooltip permanent direction="top">End</Tooltip>
        </CircleMarker>
      )}
    </MapContainer>
  )
}
