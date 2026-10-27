import { useState } from 'react'
import { INTERVALS } from '../constants'
import { toLocalInputValue } from '../format'
import PlaceInput from './PlaceInput'

// Default departure: the next full hour.
function nextHour() {
  const date = new Date(Date.now() + 60 * 60 * 1000)
  date.setMinutes(0, 0, 0)
  return toLocalInputValue(date)
}

export default function TripForm({ loading, onSubmit }) {
  const [origin, setOrigin] = useState(null)
  const [destination, setDestination] = useState(null)
  const [departure, setDeparture] = useState(nextHour())
  const [load, setLoad] = useState(35000)
  const [interval, setInterval] = useState(25)

  // The button only works after both cities were picked from the lists.
  const ready = origin && destination && departure && load !== ''

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit({
      origin: { lat: origin.lat, lng: origin.lng },
      destination: { lat: destination.lat, lng: destination.lng },
      departure: new Date(departure).toISOString(),
      load_lb: Number(load),
      interval_miles: interval,
    })
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <PlaceInput label="Origin" onSelect={setOrigin} />
      <PlaceInput label="Destination" onSelect={setDestination} />

      <div className="row">
        <label className="field">
          <span>Departure</span>
          <input type="datetime-local" value={departure} onChange={(e) => setDeparture(e.target.value)} />
        </label>
        <label className="field">
          <span>Load (lb)</span>
          <input type="number" min="0" max="100000" step="500" value={load} onChange={(e) => setLoad(e.target.value)} />
        </label>
      </div>

      <div className="field">
        <span>Weather checkpoint every</span>
        <div className="segmented">
          {INTERVALS.map((miles) => (
            <button
              type="button"
              key={miles}
              className={miles === interval ? 'active' : ''}
              onClick={() => setInterval(miles)}
            >
              {miles} mi
            </button>
          ))}
        </div>
      </div>

      <button className="primary" type="submit" disabled={!ready || loading}>
        {loading ? 'Planning…' : 'Find safest route'}
      </button>
      {!ready && <p className="hint">Type a city, then click it in the dropdown (both Origin and Destination) to enable the button.</p>}
    </form>
  )
}
