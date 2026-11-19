"""URL configuration for the Clinic Appointment Portal project."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .health import health, ready

urlpatterns = [
    path("health/", health, name="health"),                    # Module 9, Session 14
    path("ready/", ready, name="ready"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),                 # sign-up (Session 10)
    path("accounts/", include("django.contrib.auth.urls")),      # login, logout, password change and reset
    path("api/<str:version>/schema/", SpectacularAPIView.as_view(), name="schema"),           # Session 20: OpenAPI
    path("api/<str:version>/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/<str:version>/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/<str:version>/", include("api.urls")),             # the REST API: /api/v1/ and /api/v2/ (Session 20)
    path("api-auth/", include("rest_framework.urls")),           # log in and out on the browsable API
    path("", include("clinic.urls")),
]
