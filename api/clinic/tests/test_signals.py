"""Session 23: the booking confirmation is logged after the transaction commits."""
import logging

from clinic.services import book_slot


def test_booking_confirmation_is_logged(slot, asha, caplog, django_capture_on_commit_callbacks):
    caplog.set_level(logging.INFO, logger="clinic")
    with django_capture_on_commit_callbacks(execute=True):   # tests run inside a transaction that never commits
        appointment = book_slot(slot, asha)
    assert f"Booking confirmation for Asha Verma: Dr. Meera Shah on 01 Dec 2026 at 10:00 (appointment {appointment.pk})" \
        in caplog.messages


def test_status_change_sends_no_confirmation(slot, asha, caplog, django_capture_on_commit_callbacks):
    appointment = book_slot(slot, asha)
    caplog.set_level(logging.INFO, logger="clinic.signals")
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        appointment.status = "cancelled"
        appointment.save()
    assert callbacks == [] and caplog.messages == []
