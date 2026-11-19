"""Booking rules in one place, so every view (and later the API) books the same way."""
import logging

from django.core.cache import cache
from django.db import IntegrityError, transaction

from .models import Appointment, Doctor, TimeSlot

logger = logging.getLogger(__name__)        # "clinic.services", a child of the "clinic" logger (Session 12)


class SlotTaken(Exception):
    """The slot already has a booked appointment."""


def book_slot(slot, patient, reason=""):
    """Book a slot for a patient. The database constraint decides, so two people
    pressing Book at the same moment can never both succeed."""
    try:
        with transaction.atomic():
            appointment = Appointment.objects.create(slot=slot, patient=patient, reason=reason)
    except IntegrityError as e:
        if "one_active_booking_per_slot" in str(e):
            logger.warning("Slot %s was already booked; patient %s was refused", slot.pk, patient.pk)
            raise SlotTaken(f"{slot} is already booked") from e
        raise
    logger.info("Appointment %s booked: slot %s, patient %s", appointment.pk, slot.pk, patient.pk)
    return appointment


def cancel(appointment):
    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=["status"])
    logger.info("Appointment %s cancelled", appointment.pk)
    return appointment


def free_slots(doctor):
    """The doctor's slots without a booked appointment, in date and time order."""
    return doctor.slots.exclude(appointments__status=Appointment.Status.BOOKED).order_by("date", "start_time")


STATS_KEY = "clinic:stats"                  # Session 23: one name for the cached numbers


def clinic_stats():
    """The numbers on the clinic's front page. Counting runs several queries, so the result is cached
    for five minutes; the signals in clinic/signals.py delete it when an appointment changes."""
    stats = cache.get(STATS_KEY)
    if stats is not None:
        return stats, "HIT"
    stats = {
        "active_doctors": Doctor.objects.filter(is_active=True).count(),
        "free_slots": TimeSlot.objects.exclude(appointments__status=Appointment.Status.BOOKED).count(),
        "booked_appointments": Appointment.objects.filter(status=Appointment.Status.BOOKED).count(),
    }
    cache.set(STATS_KEY, stats, timeout=300)
    return stats, "MISS"
