import L from 'leaflet'
import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import '../leafletSetup' // must come before leaflet.heat
import 'leaflet.heat'
import { LEVELS, LEVEL_ORDER } from '../constants'

// Colours of the heatmap from weak (0.2) to strong (1).
const GRADIENT = { 0.2: '#e5c100', 0.45: '#f08a24', 0.7: '#d62f2f', 1: '#5b1a6b' }

// Draws the weather heatmap for one forecast hour.
// Each time `hour` changes the old layer is removed and a new one is drawn.
export default function HeatLayer({ points, hour }) {
  const map = useMap()

  useEffect(() => {
    // Each heat point is [lat, lng, strength]. Low risk has strength 0, so we skip it.
    const heatPoints = []
    for (const point of points) {
      const strength = LEVELS[LEVEL_ORDER[point.levels[hour]]].heat
      if (strength > 0) {
        heatPoints.push([point.lat, point.lng, strength])
      }
    }

    const layer = L.heatLayer(heatPoints, { radius: 32, blur: 18, max: 1, minOpacity: 0.35, gradient: GRADIENT })
    layer.addTo(map)

    // Cleanup: remove this layer before the next one is drawn.
    return () => {
      layer.remove()
    }
  }, [map, points, hour])

  return null
}
