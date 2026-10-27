"""Talks to the outside APIs and does the distance maths.

- Geocoding (city name -> lat/lng): Open-Meteo
- Routing (A -> B roads):            OSRM
- Weather forecast:                  Open-Meteo
None of them need an API key.
"""

import math
from datetime import datetime, timezone

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
ROUTE_URL = "https://router.project-osrm.org/route/v1/driving"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT = 20  # seconds to wait for an outside API
METERS_PER_MILE = 1609.344


class ApiError(Exception):
    """Raised when an outside API fails."""


def get_json(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        raise ApiError("Could not get data from " + url.split("/")[2])


# ---------------------------------------------------------------- distance maths

def distance_miles(a, b):
    """Distance between two (lat, lng) points in miles (haversine formula)."""
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 2 * 3958.8 * math.asin(math.sqrt(h))


def point_along_path(path, miles):
    """Find the (lat, lng) that is `miles` from the start of the path."""
    travelled = 0
    for i in range(1, len(path)):
        step = distance_miles(path[i - 1], path[i])
        if travelled + step >= miles:
            # The point is inside this step, so go the right fraction of the way.
            fraction = (miles - travelled) / step if step > 0 else 0
            lat = path[i - 1][0] + (path[i][0] - path[i - 1][0]) * fraction
            lng = path[i - 1][1] + (path[i][1] - path[i - 1][1]) * fraction
            return (lat, lng)
        travelled += step
    return path[-1]


def path_length(path):
    total = 0
    for i in range(1, len(path)):
        total += distance_miles(path[i - 1], path[i])
    return total


# ---------------------------------------------------------------- geocoding

def search_name(name):
    data = get_json(GEOCODE_URL, {"name": name, "count": 8, "language": "en", "format": "json"})
    places = []
    for item in data.get("results", []):
        parts = [item["name"], item.get("admin1"), item.get("country")]
        label = ", ".join(p for p in parts if p)
        places.append({"label": label, "lat": item["latitude"], "lng": item["longitude"]})
    return places


def find_places(query):
    """Search for cities. The API only knows plain names, so if "Dallas Texas" finds
    nothing we try "Dallas", and put results that mention "Texas" first."""
    words = query.replace(",", " ").split()
    for how_many in range(len(words), 0, -1):
        places = search_name(" ".join(words[:how_many]))
        if places:
            left_out = [w.lower() for w in words[how_many:]]
            matching = [p for p in places if any(w in p["label"].lower() for w in left_out)]
            others = [p for p in places if p not in matching]
            return matching + others
    return []


# ---------------------------------------------------------------- routing

def ask_osrm(points, want_alternatives):
    """Ask OSRM for routes through the given (lat, lng) points."""
    coords = ";".join(str(lng) + "," + str(lat) for lat, lng in points)
    params = {"overview": "full", "geometries": "geojson"}
    if want_alternatives:
        params["alternatives"] = "3"
    data = get_json(ROUTE_URL + "/" + coords, params)
    if data.get("code") != "Ok":
        raise ApiError("No route found between those places.")

    routes = []
    for r in data["routes"]:
        # OSRM gives (lng, lat) but we use (lat, lng).
        path = [(lat, lng) for lng, lat in r["geometry"]["coordinates"]]
        routes.append({"path": path, "miles": r["distance"] / METERS_PER_MILE, "seconds": r["duration"]})
    return routes


def get_routes(origin, destination):
    """Return up to 3 different routes from origin to destination."""
    routes = ask_osrm([origin, destination], True)[:3]
    if len(routes) == 3:
        return routes

    # OSRM often returns fewer than 3. Force different roads by going through a
    # point to the side of the middle of the trip (once each side).
    mid_lat = (origin[0] + destination[0]) / 2
    mid_lng = (origin[1] + destination[1]) / 2
    d_lat = destination[0] - origin[0]
    d_lng = destination[1] - origin[1]
    for side in (1, -1):
        via = (mid_lat - side * d_lng * 0.12, mid_lng + side * d_lat * 0.12)
        try:
            extra = ask_osrm([origin, via, destination], False)[0]
        except ApiError:
            continue  # e.g. the point is in water, just skip it

        too_long = extra["miles"] > routes[0]["miles"] * 1.5
        same_as_existing = any(
            abs(extra["miles"] - r["miles"]) < r["miles"] * 0.01 and abs(extra["seconds"] - r["seconds"]) < r["seconds"] * 0.01
            for r in routes
        )
        if len(routes) < 3 and not too_long and not same_as_existing:
            routes.append(extra)
    return routes


# ---------------------------------------------------------------- weather

def get_weather(points):
    """Hourly forecast for each (lat, lng) point, in the same order.

    Each result is a dict: start (datetime of the first hour), wind, rain, snow
    (lists with one number per hour, 72 hours starting at 00:00 UTC today).
    """
    results = []
    # Open-Meteo takes many places in one request. We send 50 at a time.
    for i in range(0, len(points), 50):
        batch = points[i : i + 50]
        data = get_json(
            WEATHER_URL,
            {
                "latitude": ",".join(str(round(p[0], 2)) for p in batch),
                "longitude": ",".join(str(round(p[1], 2)) for p in batch),
                "hourly": "wind_speed_10m,rain,showers,snowfall",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "UTC",
                "forecast_days": 3,
            },
        )
        # One place gives a dict, many places give a list.
        if isinstance(data, dict):
            data = [data]

        for place in data:
            hourly = place["hourly"]
            start = datetime.fromisoformat(hourly["time"][0]).replace(tzinfo=timezone.utc)
            rain = []
            for r, s in zip(hourly["rain"], hourly["showers"]):
                rain.append((r or 0) + (s or 0))
            results.append(
                {
                    "start": start,
                    "wind": [w or 0 for w in hourly["wind_speed_10m"]],
                    "rain": rain,
                    "snow": [s or 0 for s in hourly["snowfall"]],
                }
            )
    return results
