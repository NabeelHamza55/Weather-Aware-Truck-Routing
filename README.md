# Weather-Aware Truck Routing

A web app that helps a truck driver pick the safest route for a trip. You enter where you are going, when you
leave and how heavy the load is. The app finds three routes, checks the forecast along each one at the time
the truck will actually be there, and recommends the route with the least weather risk.

Built with React (Vite + Leaflet) for the frontend and Django for the backend.

## Running it

You need Python 3.11+ and Node 20+.

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Frontend (in a second terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server forwards `/api` requests to Django on port 8000.

Tests for the risk rules and the ranking:

```bash
cd backend
python manage.py test
```

## How it works

1. **Routes.** The backend asks OSRM for driving routes between the two places. OSRM often returns fewer than
   three, so if needed it also routes through a point to either side of the middle of the trip to get more
   options. Routes that are nearly identical or much too long are dropped.
2. **Checkpoints.** A checkpoint is placed every 10, 25 or 50 miles along each route (your choice), plus one at
   the destination.
3. **ETA.** The time the truck reaches a checkpoint is the departure time plus the route's travel time scaled by
   how far along the route the checkpoint is.
4. **Weather.** Open-Meteo gives hourly wind, rain and snow. For each checkpoint the app uses the hour of its ETA.
5. **Risk.** Each checkpoint gets the worst level of wind, rain and snow (Low, Moderate, High, Severe, No Travel),
   using the thresholds from the brief. The load rules are then applied:
   - wind of 55 mph or more is No Travel for any load
   - wind of 45-54 mph with a load over 30,000 lb is No Travel
   - wind of 35-44 mph with a load over 40,000 lb is Severe
6. **Recommendation.** Each checkpoint stands for the road halfway to its neighbours, which gives miles at each
   risk level per route. Routes are ranked by fewest Severe miles, then fewest High miles, then lowest average
   risk, then shortest travel time. Routes with any No Travel stretch are put behind the others.
7. **Heatmap.** The forecast fetched for each checkpoint covers about 72 hours, so the server also works out the
   risk for each of the next 49 hours and sends it along with the routes. The slider on the page only switches
   between those hours, so it does not make any more requests.

## Project layout

```
backend/routing/
  risk.py       risk rules
  services.py   OSRM and Open-Meteo calls, distance maths
  planner.py    checkpoints, summaries, ranking, heatmap data
  views.py      the two API endpoints
  tests.py
frontend/src/
  App.jsx       page state
  components/   form, route cards, map, heat layer, slider
```

API:

- `GET /api/geocode?q=dallas` returns matching places
- `POST /api/plan` takes `origin`, `destination` (each `{lat, lng}`), `departure` (ISO time), `load_lb` and
  `interval_miles`, and returns the routes, the recommended route id and the heatmap data

## Assumptions

- A value exactly on a boundary goes to the higher level (25 mph is Moderate, 35 mph is High). Exactly 1.00 in/hr
  of rain and 3.0 in/hr of snow count as Severe.
- Wind is the average 10 m wind speed, not gusts. Rain is Open-Meteo's `rain` plus `showers`.
- Travel speed is assumed steady along the route, so ETAs ignore traffic, breaks and speed changes.
- The heatmap shows nothing for Low risk, so a clear corridor means calm weather.
- The forecast data covers about 72 hours from midnight UTC today. If an ETA falls outside that, the last
  available hour is used and the checkpoint popup says so.

## Limitations

- OSRM uses a car profile, so there are no truck height or weight restrictions.
- The public OSRM server is rate limited. Set `OSRM_BASE_URL` to your own instance for heavier use.
- Place search only understands city names, not street addresses.
- Requests take a few seconds because the outside APIs are called one after another.
- The heatmap only covers points along the routes, and it gets denser with a smaller checkpoint interval.

## Deploying

Backend: install `requirements.txt` and run `gunicorn config.wsgi`. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`,
`DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` (the frontend URL).

Frontend: `npm run build`, publish the `dist` folder, and set `VITE_API_URL` to the backend URL.
