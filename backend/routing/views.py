import json
from datetime import datetime, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import planner, services


def geocode(request):
    """GET /api/geocode?q=dallas  ->  list of matching places."""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    try:
        return JsonResponse(services.find_places(query), safe=False)
    except services.ApiError as error:
        return JsonResponse({"detail": str(error)}, status=502)


@csrf_exempt
def plan_routes(request):
    """POST /api/plan  ->  3 routes with weather risk, a recommendation and heatmap data."""
    if request.method != "POST":
        return JsonResponse({"detail": "Use POST."}, status=405)

    # Read and check the data the user sent.
    try:
        body = json.loads(request.body)
        origin = (float(body["origin"]["lat"]), float(body["origin"]["lng"]))
        destination = (float(body["destination"]["lat"]), float(body["destination"]["lng"]))
        load = int(body["load_lb"])
        interval = int(body.get("interval_miles", 25))
        departure = datetime.fromisoformat(body["departure"].replace("Z", "+00:00"))
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"detail": "Please fill in every field correctly."}, status=400)

    if interval not in (10, 25, 50):
        return JsonResponse({"detail": "Checkpoint interval must be 10, 25 or 50 miles."}, status=400)
    if load < 0 or load > 100000:
        return JsonResponse({"detail": "Load must be between 0 and 100,000 lb."}, status=400)
    if departure.tzinfo is None:
        departure = departure.replace(tzinfo=timezone.utc)

    try:
        result = planner.plan(origin, destination, departure.astimezone(timezone.utc), load, interval)
    except services.ApiError as error:
        return JsonResponse({"detail": str(error)}, status=502)
    return JsonResponse(result)
