"""Module 9, Session 09: factories. Each one makes a valid row with sensible values,
and the rows it depends on as well: AppointmentFactory() also makes a patient with a
login, a slot, a doctor and a speciality. A test sets only what matters to it:
AppointmentFactory(status="cancelled"). No login has a password."""
from datetime import date, time

import factory

from accounts.models import User
from clinic.models import Appointment, Doctor, Patient, Speciality, TimeSlot
from clinic.roles import create_groups


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ["username"]       # the same name twice: one user
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    role = User.Role.PATIENT
    password = factory.django.Password(None)      # None: an unusable password

    @factory.post_generation
    def group(user, create, name, **kwargs):      # UserFactory(group="Reception")
        if create and name:
            user.groups.add(create_groups()[name])


class SpecialityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Speciality
        django_get_or_create = ["slug"]

    name = "General Medicine"
    slug = factory.LazyAttribute(lambda s: s.name.lower().replace(" ", "-"))


class DoctorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Doctor

    name = factory.Sequence(lambda n: f"Dr. Test {n:02}")
    speciality = factory.SubFactory(SpecialityFactory)
    fee = 500


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Patient {n:02}")
    phone = "98250 00000"


class SlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeSlot

    doctor = factory.SubFactory(DoctorFactory)
    date = date(2026, 12, 1)
    start_time = factory.Iterator(
        [time(10, 0), time(10, 30), time(11, 0), time(11, 30)])


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    slot = factory.SubFactory(SlotFactory)
    patient = factory.SubFactory(PatientFactory)
    reason = "Check-up"


def doctor_with_login(username, **fields):
    """A doctor who can log in (role doctor, group Doctors)."""
    user = UserFactory(username=username, role=User.Role.DOCTOR, group="Doctors")
    return DoctorFactory(user=user, **fields)
