from django.http import JsonResponse
from django.urls import include, path


def index(request):
    return JsonResponse(
        {
            "service": "Weather-Aware Truck Routing API",
            "endpoints": {"geocode": "GET /api/geocode?q=<text>", "plan": "POST /api/plan"},
        }
    )


urlpatterns = [
    path("", index),
    path("api/", include("routing.urls")),
]
