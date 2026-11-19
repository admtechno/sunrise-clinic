"""Module 9, Session 09: what one factory call makes."""
from clinic.models import Appointment, Doctor, Patient, Speciality, TimeSlot

from .factories import AppointmentFactory, DoctorFactory, SlotFactory

MODELS = [Speciality, Doctor, TimeSlot, Patient, Appointment]


def counts():
    return {m.__name__: m.objects.count() for m in MODELS}


def test_one_appointment_makes_every_row_it_needs(db):
    appointment = AppointmentFactory()
    print(f"\n{appointment}\n{counts()}")
    assert counts() == {"Speciality": 1, "Doctor": 1, "TimeSlot": 1,
                        "Patient": 1, "Appointment": 1}
    assert appointment.patient.user.has_usable_password() is False


def test_a_test_sets_only_what_matters_to_it(db):
    cancelled = AppointmentFactory(status="cancelled", slot__doctor__fee=900)
    assert (cancelled.status, cancelled.slot.doctor.fee) == ("cancelled", 900)


def test_many_rows_in_one_line(db):
    slots = SlotFactory.create_batch(4, doctor=DoctorFactory(name="Dr. Busy"))
    times = sorted(f"{s.start_time:%H:%M}" for s in slots)
    # the Iterator goes on from where the last test left it: check WHICH times,
    # not their order
    assert times == ["10:00", "10:30", "11:00", "11:30"]
    assert Speciality.objects.count() == 1         # get_or_create: one speciality
