"""Session 23: GET /api/v1/stats/ - three numbers for a dashboard, from the cache when possible."""
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from clinic.services import clinic_stats


@extend_schema(summary="Clinic numbers", responses=inline_serializer("Stats", {
    "active_doctors": serializers.IntegerField(), "free_slots": serializers.IntegerField(),
    "booked_appointments": serializers.IntegerField()}))
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def stats(request, **kwargs):                            # kwargs: the version from the URL (Session 20)
    data, source = clinic_stats()
    return Response(data, headers={"X-Cache": source})   # HIT: from the cache, MISS: counted now
