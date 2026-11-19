"""Session 13: the booking rules (Session 06) as automated tests."""
from datetime import time

import pytest
from django.db import IntegrityError

from clinic.models import Appointment, TimeSlot
from clinic.services import SlotTaken, book_slot, cancel, free_slots


def test_book_a_free_slot(slot, asha):
    appointment = book_slot(slot, asha, reason="Fever")
    assert appointment.status == Appointment.Status.BOOKED
    assert list(free_slots(slot.doctor)) == []


def test_no_double_booking(slot, asha, ravi):
    book_slot(slot, asha)
    with pytest.raises(SlotTaken):
        book_slot(slot, ravi)
    assert Appointment.objects.filter(slot=slot).count() == 1


def test_cancel_frees_the_slot(slot, asha, ravi):
    cancel(book_slot(slot, asha))
    book_slot(slot, ravi)                            # the slot can be booked again
    assert Appointment.objects.get(slot=slot, status="booked").patient == ravi


def test_slot_outside_opening_hours_is_refused(doctor, slot):
    with pytest.raises(IntegrityError, match="slot_in_opening_hours"):
        TimeSlot.objects.create(doctor=doctor, date=slot.date, start_time=time(21, 0))
