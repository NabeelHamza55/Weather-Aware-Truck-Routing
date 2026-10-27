import { useState } from 'react'
import { planRoutes } from './api'
import HeatmapControl from './components/HeatmapControl'
import MapView from './components/MapView'
import RouteList from './components/RouteList'
import TripForm from './components/TripForm'

export default function App() {
  const [result, setResult] = useState(null)
  const [trip, setTrip] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [heatHour, setHeatHour] = useState(0)
  const [showHeat, setShowHeat] = useState(true)

  async function handleSubmit(payload) {
    setLoading(true)
    setError(null)
    try {
      const data = await planRoutes(payload)
      setResult(data)
      setTrip(payload)
      setSelectedId(data.recommended_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Weather-Aware Truck Routing</h1>
        <TripForm loading={loading} onSubmit={handleSubmit} />

        {error && <p className="error">{error}</p>}

        {result && (
          <>
            <p className="recommendation">{result.recommendation}</p>
            <RouteList
              routes={result.routes}
              recommendedId={result.recommended_id}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
            <HeatmapControl
              heatmap={result.heatmap}
              hour={heatHour}
              onHour={setHeatHour}
              show={showHeat}
              onShow={setShowHeat}
            />
          </>
        )}
      </aside>

      <main>
        <MapView
          result={result}
          selectedId={selectedId}
          onSelect={setSelectedId}
          heatHour={heatHour}
          showHeat={showHeat}
          origin={trip?.origin}
          destination={trip?.destination}
        />
      </main>
    </div>
  )
}
