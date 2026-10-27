"""Builds the route options: checkpoints, ETAs, risk, ranking and heatmap data."""

from datetime import datetime, timedelta, timezone

from . import risk, services

HEATMAP_HOURS = 49  # slider goes from 0 to 48 hours


def hour_number(when, forecast):
    """Which hour of the forecast is this time? Returns (number, was_out_of_range)."""
    hours = int((when - forecast["start"]).total_seconds() // 3600)
    last = len(forecast["wind"]) - 1
    if hours < 0:
        return 0, True
    if hours > last:
        return last, True
    return hours, False


def make_checkpoints(route, interval, departure, load):
    """Pick a point every `interval` miles and check the weather there."""
    path = route["path"]
    total = services.path_length(path)

    # Mile markers: 0, interval, 2*interval ... and finally the destination.
    miles_list = []
    mile = 0
    while mile < total:
        miles_list.append(mile)
        mile += interval
    miles_list.append(total)

    points = [services.point_along_path(path, m) for m in miles_list]
    forecasts = services.get_weather(points)

    checkpoints = []
    for i in range(len(miles_list)):
        mile = miles_list[i]
        forecast = forecasts[i]

        # When will the truck get here? Assume a steady speed over the whole route.
        eta = departure + timedelta(seconds=route["seconds"] * mile / total)
        hour, out_of_range = hour_number(eta, forecast)
        wind = forecast["wind"][hour]
        rain = forecast["rain"][hour]
        snow = forecast["snow"][hour]
        level = risk.get_risk(wind, rain, snow, load)

        # Each checkpoint covers the road up to halfway to its neighbours.
        miles_covered = 0
        if i > 0:
            miles_covered += (mile - miles_list[i - 1]) / 2
        if i < len(miles_list) - 1:
            miles_covered += (miles_list[i + 1] - mile) / 2

        checkpoints.append(
            {
                "lat": points[i][0],
                "lng": points[i][1],
                "mile": round(mile, 1),
                "eta": eta.isoformat(),
                "wind_mph": round(wind, 1),
                "rain_in_hr": round(rain, 2),
                "snow_in_hr": round(snow, 2),
                "level": risk.LEVEL_NAMES[level],
                "score": level,
                "miles_covered": miles_covered,
                "forecast_out_of_range": out_of_range,
            }
        )
    return checkpoints, forecasts


def make_summary(route, checkpoints):
    """Add up the miles at each risk level for one route."""
    miles_by_level = {name: 0 for name in risk.LEVEL_NAMES}
    total_covered = 0
    weighted_score = 0
    worst = 0
    for c in checkpoints:
        miles_by_level[c["level"]] += c["miles_covered"]
        total_covered += c["miles_covered"]
        weighted_score += c["score"] * c["miles_covered"]
        worst = max(worst, c["score"])

    for name in miles_by_level:
        miles_by_level[name] = round(miles_by_level[name], 1)

    return {
        "distance_miles": round(route["miles"], 1),
        "duration_minutes": round(route["seconds"] / 60),
        "miles_by_level": miles_by_level,
        "avg_risk": round(weighted_score / total_covered, 2) if total_covered else 0,
        "worst_level": risk.LEVEL_NAMES[worst],
    }


def ranking_key(route):
    """Smaller is better. This follows the assessment's order of preference:
    fewest Severe miles, fewest High miles, lowest average risk, shortest time.
    No Travel miles come first because a route with No Travel can't be driven."""
    s = route["summary"]
    m = s["miles_by_level"]
    return (m["no_travel"], m["severe"], m["high"], s["avg_risk"], s["duration_minutes"])


def make_heatmap(all_checkpoints, all_forecasts, load):
    """For every checkpoint, the risk level for each of the next 49 hours."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    points = []
    for checkpoints, forecasts in zip(all_checkpoints, all_forecasts):
        for c, forecast in zip(checkpoints, forecasts):
            first_hour, _ = hour_number(now, forecast)
            levels = []
            for h in range(HEATMAP_HOURS):
                i = min(first_hour + h, len(forecast["wind"]) - 1)
                levels.append(risk.get_risk(forecast["wind"][i], forecast["rain"][i], forecast["snow"][i], load))
            points.append({"lat": c["lat"], "lng": c["lng"], "levels": levels})
    return {"start": now.isoformat(), "hours": HEATMAP_HOURS, "points": points}


def plan(origin, destination, departure, load, interval):
    routes = services.get_routes(origin, destination)

    results = []
    all_checkpoints = []
    all_forecasts = []
    for i, route in enumerate(routes):
        checkpoints, forecasts = make_checkpoints(route, interval, departure, load)
        all_checkpoints.append(checkpoints)
        all_forecasts.append(forecasts)
        results.append(
            {
                "id": i,
                "name": "Route " + "ABC"[i],
                "path": [[round(lat, 5), round(lng, 5)] for lat, lng in route["path"]],
                "summary": make_summary(route, checkpoints),
                "checkpoints": checkpoints,
            }
        )

    # Rank the routes: best first.
    ranked = sorted(results, key=ranking_key)
    for position, route in enumerate(ranked):
        route["rank"] = position + 1
        route["driveable"] = route["summary"]["miles_by_level"]["no_travel"] == 0

    best = ranked[0]
    return {
        "recommended_id": best["id"],
        "recommendation": explain(best, ranked),
        "routes": results,
        "heatmap": make_heatmap(all_checkpoints, all_forecasts, load),
    }


def explain(best, ranked):
    if not best["driveable"]:
        return "Every route has No Travel conditions. Consider leaving at a different time."

    miles = best["summary"]["miles_by_level"]
    text = "%s is recommended: %s severe miles, %s high-risk miles, %s min." % (
        best["name"],
        miles["severe"],
        miles["high"],
        best["summary"]["duration_minutes"],
    )
    if len(ranked) > 1:
        slower_by = best["summary"]["duration_minutes"] - ranked[1]["summary"]["duration_minutes"]
        if slower_by > 0:
            text += " It is %d min slower than %s but has less weather risk." % (slower_by, ranked[1]["name"])
    return text
