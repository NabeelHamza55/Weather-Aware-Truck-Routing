import { useState } from 'react'
import { searchPlaces } from '../api'

// A text box that shows a list of matching cities while you type.
// When the user clicks a city, we call onSelect(place). Typing again calls onSelect(null).
export default function PlaceInput({ label, onSelect }) {
  const [text, setText] = useState('')
  const [places, setPlaces] = useState([])
  const [message, setMessage] = useState('')
  const [showList, setShowList] = useState(false)

  function handleChange(event) {
    const newText = event.target.value
    setText(newText)
    onSelect(null) // the old choice no longer matches the text
    setShowList(true)

    if (newText.trim().length < 3) {
      setPlaces([])
      setMessage('Type at least 3 letters')
      return
    }

    setMessage('Searching...')
    searchPlaces(newText.trim())
      .then((results) => {
        setPlaces(results)
        setMessage(results.length === 0 ? 'No city found. Try just the city name.' : '')
      })
      .catch(() => {
        setPlaces([])
        setMessage('Could not reach the server. Is the backend running on port 8000?')
      })
  }

  function choosePlace(place) {
    setText(place.label)
    setShowList(false)
    onSelect(place)
  }

  return (
    <label className="field place">
      <span>{label}</span>
      <input
        value={text}
        placeholder="City, e.g. Dallas or Houston TX"
        onChange={handleChange}
        onBlur={() => setTimeout(() => setShowList(false), 150)}
      />
      {showList && text !== '' && (
        <ul className="suggestions">
          {message && <li className="note">{message}</li>}
          {places.map((place) => (
            <li key={place.lat + ',' + place.lng} onMouseDown={() => choosePlace(place)}>
              {place.label}
            </li>
          ))}
        </ul>
      )}
    </label>
  )
}
