"""Session 18: who am I? The same answer for a session cookie and for a JWT.
Session 19: the token view is throttled, so passwords cannot be guessed quickly.
Session 20: extend_schema() describes the function view for the OpenAPI schema."""
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MeSerializer


@extend_schema(responses=MeSerializer, summary="Who am I?")
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request, **kwargs):   # kwargs: the version from the URL (Session 20)
    user = request.user
    return Response({
        "username": user.username,
        "role": user.role,
        "groups": sorted(user.groups.values_list("name", flat=True)),
        "is_patient": hasattr(user, "patient"),
        "authenticated_by": type(request.successful_authenticator).__name__,   # which class let them in
    })


class LoginView(TokenObtainPairView):
    throttle_scope = "login"                                 # ScopedRateThrottle: rate from DEFAULT_THROTTLE_RATES
