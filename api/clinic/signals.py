"""Session 23: things that should happen whenever an appointment is saved, wherever it is saved from
(the website, the API, the admin, a script). Connected in ClinicConfig.ready() (clinic/apps.py)."""
import logging

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Appointment, TimeSlot
from .services import STATS_KEY

logger = logging.getLogger("clinic.signals")


@receiver(post_save, sender=Appointment)
def appointment_saved(sender, instance, created, raw=False, **kwargs):
    if raw:                                              # loaddata: rows from a fixture, not a real booking
        return
    cache.delete(STATS_KEY)                              # the cached numbers are out of date now
    if created:                                          # a new booking, not a status change
        # on_commit: only after the booking is really in the database (book_slot() uses a transaction)
        transaction.on_commit(lambda: logger.info(
            "Booking confirmation for %s: %s on %s at %s (appointment %s)", instance.patient.name,
            instance.slot.doctor.name, f"{instance.slot.date:%d %b %Y}", f"{instance.slot.start_time:%H:%M}", instance.pk))


@receiver(post_save, sender=TimeSlot)
def slot_saved(sender, **kwargs):
    cache.delete(STATS_KEY)                              # a new slot changes "free_slots"
