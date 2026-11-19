import uuid
from datetime import time
from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .validators import REPORT_TYPES, validate_report_content, validate_report_size


class Speciality(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "specialities"

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT, related_name="doctors")
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="doctor")    # login account, Session 11

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.speciality})"


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="patient")   # login account, Session 10
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="slots")
    date = models.DateField()
    start_time = models.TimeField()

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "date", "start_time"], name="unique_slot_per_doctor"),
            models.CheckConstraint(condition=models.Q(start_time__gte=time(8, 0), start_time__lte=time(20, 0)),
                                   name="slot_in_opening_hours"),
        ]

    def __str__(self):
        return f"{self.doctor.name}, {self.date:%d %b %Y} {self.start_time:%H:%M}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slot__date", "slot__start_time"]
        constraints = [
            # No double booking: at most one *booked* appointment per slot (a partial unique index).
            # Cancelled appointments do not count, so a cancelled slot can be booked again.
            models.UniqueConstraint(fields=["slot"], condition=models.Q(status="booked"),
                                    name="one_active_booking_per_slot",
                                    violation_error_message="This time slot is already booked."),
        ]

    def __str__(self):
        return f"{self.patient} with {self.slot} ({self.status})"


def report_path(instance, filename):
    """Store reports under a random name: users cannot guess or overwrite each other's files."""
    return f"reports/{instance.appointment_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class Report(models.Model):
    """Session 12: a file (lab result, scan) that a patient uploads for an appointment."""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="reports")
    file = models.FileField(upload_to=report_path, validators=[
        FileExtensionValidator(REPORT_TYPES), validate_report_size, validate_report_content])
    original_name = models.CharField(max_length=200)        # shown to people; never used as a path
    size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return self.original_name
