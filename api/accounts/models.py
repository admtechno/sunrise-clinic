from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """The portal's user. Created in Session 04, before the first migrate, so it can grow later."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
