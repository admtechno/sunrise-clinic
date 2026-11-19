from django.contrib import admin, messages

from .models import Appointment, Doctor, Patient, Report, Speciality, TimeSlot
from .services import cancel

admin.site.site_header = "Sunrise Clinic administration"
admin.site.site_title = "Sunrise Clinic admin"
admin.site.index_title = "Clinic data"


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}        # the slug is typed for you from the name
    search_fields = ["name"]


class TimeSlotInline(admin.TabularInline):           # a doctor's slots, edited on the doctor's page
    model = TimeSlot
    extra = 1
    ordering = ["date", "start_time"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["name", "speciality", "fee", "is_active"]
    list_filter = ["speciality", "is_active"]
    search_fields = ["name", "speciality__name"]
    list_editable = ["fee", "is_active"]
    list_select_related = ["speciality"]
    inlines = [TimeSlotInline]
    fieldsets = [
        (None, {"fields": ["name", "speciality", "fee", "is_active"]}),
        ("Profile", {"fields": ["bio"], "classes": ["collapse"]}),
        ("Login", {"fields": ["user"]}),                # Session 11: the doctor's own account
    ]
    raw_id_fields = ["user"]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "date_of_birth", "user"]
    search_fields = ["name", "phone"]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["doctor", "date", "start_time", "is_booked"]
    list_filter = ["date", "doctor__speciality"]
    date_hierarchy = "date"
    list_select_related = ["doctor"]

    @admin.display(boolean=True, description="Booked")
    def is_booked(self, obj):
        return obj.appointments.filter(status=Appointment.Status.BOOKED).exists()


class ReportInline(admin.TabularInline):              # Session 12: an appointment's reports
    model = Report
    extra = 0
    fields = ["original_name", "size", "uploaded_at"]
    readonly_fields = fields                         # files are uploaded by patients, not here


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    inlines = [ReportInline]
    list_display = ["patient", "slot", "status", "created_at"]
    list_filter = ["status", "slot__doctor"]
    search_fields = ["patient__name", "slot__doctor__name"]
    readonly_fields = ["created_at"]
    list_select_related = ["patient", "slot__doctor"]
    actions = ["cancel_appointments"]

    @admin.action(description="Cancel selected appointments")
    def cancel_appointments(self, request, queryset):
        booked = queryset.filter(status=Appointment.Status.BOOKED)
        for appointment in booked:
            cancel(appointment)                     # the same service the portal uses
        self.message_user(request, f"{len(booked)} appointment(s) cancelled.", messages.SUCCESS)
