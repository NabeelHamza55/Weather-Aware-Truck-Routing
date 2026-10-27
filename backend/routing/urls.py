from django.urls import path

from . import views

urlpatterns = [
    path("geocode", views.geocode),
    path("plan", views.plan_routes),
]
