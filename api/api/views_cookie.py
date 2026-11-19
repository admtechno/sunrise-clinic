"""Module 9, Session 05: login for the browser.

The refresh token lives in an HttpOnly cookie that page scripts cannot read; the
access token is in the JSON answer and stays in the page's memory. Every cookie
request must carry the header X-Clinic-Client: desk. A form on another site
cannot add a header, and a script on another origin needs CORS permission first,
so the cookie alone is never enough (protection against CSRF).
Session 09: @extend_schema describes these views in the OpenAPI schema, which the
contract tests read; it changes nothing in what they do."""
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import exceptions, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

COOKIE = "clinic_refresh"
COOKIE_PATH = "/api/v1/auth/cookie/"  # the browser sends it to these three views only
HEADER = "HTTP_X_CLINIC_CLIENT"  # X-Clinic-Client, as Django names it in request.META
ACCESS = inline_serializer("CookieAccess", {"access": serializers.CharField()})
LOGIN = inline_serializer("CookieLogin", {
    "username": serializers.CharField(), "password": serializers.CharField()})


def set_refresh_cookie(response, refresh):
    response.set_cookie(
        COOKIE, str(refresh),
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path=COOKIE_PATH,
        httponly=True,                        # document.cookie cannot see it
        secure=settings.JWT_COOKIE_SECURE,    # HTTPS only in production
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


class CookieView(APIView):
    authentication_classes = []               # these views read the cookie themselves
    permission_classes = [AllowAny]

    def get_authenticate_header(self, request):
        # without authentication classes DRF would turn every 401 into a 403;
        # this keeps the 401
        return 'Bearer realm="api"'

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.META.get(HEADER) != "desk":
            raise exceptions.PermissionDenied(
                "The header X-Clinic-Client: desk is missing."
            )

    def cookie_token(self, request):
        value = request.COOKIES.get(COOKIE)
        if not value:
            raise exceptions.NotAuthenticated("No refresh cookie. Please log in.")
        return value


class CookieLoginView(CookieView):
    """POST {username, password} -> 200 {access} and the refresh cookie."""
    throttle_scope = "login"                  # the same 5 a minute as /auth/token/

    @extend_schema(request=LOGIN, responses={200: ACCESS}, summary="Log in (cookie)")
    def post(self, request, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise exceptions.AuthenticationFailed(str(e))
        response = Response({"access": serializer.validated_data["access"]})
        set_refresh_cookie(response, serializer.validated_data["refresh"])
        return response


class CookieRefreshView(CookieView):
    """POST (no body) -> 200 {access} and a NEW refresh cookie.

    The old refresh token stops working (rotation and blacklist in settings)."""

    @extend_schema(request=None, responses={200: ACCESS}, summary="New access token")
    def post(self, request, **kwargs):
        token = self.cookie_token(request)
        serializer = TokenRefreshSerializer(data={"refresh": token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise exceptions.AuthenticationFailed(str(e), code="token_not_valid")
        response = Response({"access": serializer.validated_data["access"]})
        # the new refresh token (rotation)
        set_refresh_cookie(response, serializer.validated_data["refresh"])
        return response


class CookieLogoutView(CookieView):
    """POST -> 204: the refresh token is blacklisted and the cookie removed."""

    @extend_schema(request=None, summary="Log out (cookie)",
                   responses={204: OpenApiResponse(description="Logged out")})
    def post(self, request, **kwargs):
        value = request.COOKIES.get(COOKIE)
        if value:
            try:
                RefreshToken(value).blacklist()
            except TokenError:
                pass  # already expired or blacklisted: logging out still works
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            COOKIE, path=COOKIE_PATH, samesite=settings.JWT_COOKIE_SAMESITE
        )
        return response
