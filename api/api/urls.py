"""The router makes every URL of the four viewsets, plus an API root page (Session 15).
Session 18 adds the JWT endpoints and /me/, Session 19 the doctor's schedule."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views, views_auth, views_cookie, views_stats

app_name = "api"

router = DefaultRouter()
router.register("specialities", views.SpecialityViewSet)
router.register("doctors", views.DoctorViewSet)
router.register("slots", views.SlotViewSet)
router.register("appointments", views.AppointmentViewSet, basename="appointment")   # no queryset attribute
router.register("doctor/schedule", views.DoctorScheduleViewSet, basename="doctor-schedule")   # Session 19
urlpatterns = [
    path("auth/token/", views_auth.LoginView.as_view(), name="token_obtain_pair"),     # username + password, throttled
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),    # refresh -> new access
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", views_auth.me, name="me"),
    # Module 9, Session 05: the browser login, refresh token in an HttpOnly cookie
    path("auth/cookie/login/", views_cookie.CookieLoginView.as_view(),
         name="cookie_login"),
    path("auth/cookie/refresh/", views_cookie.CookieRefreshView.as_view(),
         name="cookie_refresh"),
    path("auth/cookie/logout/", views_cookie.CookieLogoutView.as_view(),
         name="cookie_logout"),
    path("stats/", views_stats.stats, name="stats"),                             # Session 23
] + router.urls
