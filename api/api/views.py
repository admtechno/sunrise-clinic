"""Session 20: the API of Sessions 15 to 19, documented, with a version 2 of the doctors."""
from django.db.models import Exists, OuterRef, ProtectedError, Value
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from clinic.models import Appointment, Doctor, Speciality, TimeSlot
from clinic.services import cancel, free_slots

from .exceptions import Conflict
from .filters import DoctorFilter, SlotFilter
from .permissions import IsDoctor, IsOwnerOrReception, IsPatient, IsSlotDoctor, ReportRules
from .serializers import (AppointmentSerializer, BookingSerializer, DoctorSerializer, DoctorV2Serializer,
                          ReportSerializer, SlotSerializer, SpecialitySerializer)

BOOKED = Appointment.objects.filter(status=Appointment.Status.BOOKED, slot=OuterRef("pk"))
STAFF_RULES = [permissions.DjangoModelPermissionsOrAnonReadOnly]   # read: everyone; write: model permissions (Session 11)


class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = STAFF_RULES

    @method_decorator(cache_page(60))                        # Session 23: the whole answer, for 60 seconds
    def list(self, request, *args, **kwargs):                # specialities change a few times a year
        return super().list(request, *args, **kwargs)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related("speciality")
    serializer_class = DoctorSerializer
    permission_classes = STAFF_RULES
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DoctorFilter                           # ?speciality=  ?max_fee=
    search_fields = ["name", "bio", "speciality__name"]      # ?search=
    ordering_fields = ["name", "fee"]                        # ?ordering=fee  ?ordering=-fee
    ordering = ["name"]

    def get_serializer_class(self):                          # Session 20: request.version is "v1" or "v2"
        if self.request.version == "v2" and self.request.method in permissions.SAFE_METHODS:
            return DoctorV2Serializer                        # v2 changes how doctors are shown; writes are as in v1
        return DoctorSerializer

    # Session 09: the schema said "one doctor"; the answer is a list of slots,
    # and each slot now says booked: false, as the schema promises
    @extend_schema(responses=SlotSerializer(many=True))
    @action(detail=True, pagination_class=None)              # GET /api/v1/doctors/<id>/slots/
    def slots(self, request, pk=None, **kwargs):   # kwargs: the version from the URL (Session 20)
        doctor = self.get_object()
        slots = free_slots(doctor).select_related("doctor").annotate(booked=Value(False))
        return Response(SlotSerializer(slots, many=True).data)


class SlotViewSet(viewsets.ModelViewSet):
    serializer_class = SlotSerializer
    permission_classes = STAFF_RULES
    queryset = TimeSlot.objects.select_related("doctor").annotate(booked=Exists(BOOKED))
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SlotFilter                             # replaces the hand-written get_queryset() of Session 15
    ordering_fields = ["date", "start_time"]
    ordering = ["date", "start_time"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:                               # Appointment.slot uses on_delete=PROTECT
            raise Conflict("This slot has appointments and cannot be deleted.")   # through json_errors


class AppointmentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Patients see their own appointments and book with POST; users with clinic.view_appointment see all."""
    RULES = {                                                # Session 19: permissions per action
        "create": [permissions.IsAuthenticated, IsPatient],
        "cancel": [permissions.IsAuthenticated, IsOwnerOrReception],
        "complete": [permissions.IsAuthenticated, IsDoctor, IsSlotDoctor],
        "reports": [permissions.IsAuthenticated, ReportRules],   # Module 9, S07
    }

    def get_permissions(self):
        return [rule() for rule in self.RULES.get(self.action, [permissions.IsAuthenticated])]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):        # Session 20: schema generation has no real user
            return Appointment.objects.none()
        appointments = Appointment.objects.select_related("slot__doctor", "patient")
        if not self.request.user.has_perm("clinic.view_appointment"):
            appointments = appointments.filter(patient__user=self.request.user)
        return appointments

    def get_serializer_class(self):                          # one serializer to write, another to read
        booking = self.action == "create" or (self.action == "list" and self.request.method == "POST")
        return BookingSerializer if booking else AppointmentSerializer

    @extend_schema(request=BookingSerializer, responses={201: AppointmentSerializer},   # Session 20: create answers
                   summary="Book a slot")                                                # with the read serializer
    def create(self, request, *args, **kwargs):
        booking = self.get_serializer(data=request.data)     # BookingSerializer, with the request in its context
        booking.is_valid(raise_exception=True)              # 400 with the field errors
        appointment = booking.save()                         # BookingSerializer.create() -> book_slot()
        appointment = self.get_queryset().get(pk=appointment.pk)
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    def change_status(self, new_status):
        appointment = self.get_object()                      # 404 if not in get_queryset(), then the object permissions
        if appointment.status != Appointment.Status.BOOKED:
            raise Conflict(f"This appointment is already {appointment.status}.")
        if new_status == Appointment.Status.CANCELLED:
            cancel(appointment)
        else:
            appointment.status = new_status
            appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"])                   # POST /api/v1/appointments/<id>/cancel/
    def cancel(self, request, pk=None, **kwargs):   # kwargs: the version from the URL (Session 20)
        return self.change_status(Appointment.Status.CANCELLED)

    @action(detail=True, methods=["post"])                   # POST /api/v1/appointments/<id>/complete/
    def complete(self, request, pk=None, **kwargs):   # kwargs: the version from the URL (Session 20)
        return self.change_status(Appointment.Status.COMPLETED)

    # Module 9, Session 07: GET and POST /api/v1/appointments/<id>/reports/
    @extend_schema(request={"multipart/form-data": ReportSerializer},
                   responses={200: ReportSerializer(many=True),
                              201: ReportSerializer})
    # Session 09: pagination_class=None. The answer is a plain list, and the contract
    # test showed that the schema promised pages
    @action(detail=True, methods=["get", "post"], pagination_class=None,
            parser_classes=[MultiPartParser])  # a file, not JSON
    def reports(self, request, pk=None, **kwargs):
        appointment = self.get_object()  # 404, then ReportRules
        if request.method == "GET":
            data = ReportSerializer(appointment.reports.all(), many=True).data
            return Response(data)
        report = ReportSerializer(data=request.data,
                                  context={"appointment": appointment})
        report.is_valid(raise_exception=True)  # 400 with the file's errors
        report.save()
        return Response(report.data, status=status.HTTP_201_CREATED)


class DoctorScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/doctor/schedule/: the logged-in doctor's appointments, and nobody else's."""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):        # Session 20: schema generation has no real user
            return Appointment.objects.none()
        return Appointment.objects.filter(slot__doctor=self.request.user.doctor).select_related("slot__doctor", "patient")
