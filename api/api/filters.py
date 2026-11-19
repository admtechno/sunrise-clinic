"""Session 17: the query-string filters of the API, written with django-filter."""
import django_filters
from django.db.models import Q

from clinic.models import Doctor, TimeSlot


class DoctorFilter(django_filters.FilterSet):
    speciality = django_filters.CharFilter(field_name="speciality__slug")          # ?speciality=dermatology
    max_fee = django_filters.NumberFilter(field_name="fee", lookup_expr="lte")     # ?max_fee=600

    class Meta:
        model = Doctor
        fields = ["speciality", "max_fee"]


class SlotFilter(django_filters.FilterSet):
    doctor = django_filters.NumberFilter(field_name="doctor_id")                    # ?doctor=1
    speciality = django_filters.CharFilter(field_name="doctor__speciality__slug")   # ?speciality=paediatrics
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")     # ?date_from=2026-12-02
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    free = django_filters.BooleanFilter(method="filter_free")                       # ?free=true

    class Meta:
        model = TimeSlot
        fields = ["doctor", "speciality", "date_from", "date_to", "free"]

    def filter_free(self, queryset, name, value):        # "booked" is the viewset's annotation
        return queryset.filter(booked=not value)
