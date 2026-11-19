"""Session 22: fixtures for the API tests. pytest finds them by name; every test gets fresh rows
in the test database, rolled back afterwards. No login has a password (set_unusable_password)."""
from datetime import date, time

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from accounts.models import User
from clinic.models import Appointment, Doctor, Patient, Speciality, TimeSlot
from clinic.roles import create_groups


@pytest.fixture(autouse=True)
def clear_throttle_counts():                     # autouse: runs for every test in api/tests/
    cache.clear()                                # DRF keeps throttle counts in the cache (Session 19)


@pytest.fixture
def api():                                       # a DRF test client that is not logged in
    return APIClient()


def make_user(username, role=User.Role.PATIENT, group=None):
    user = User.objects.create(username=username, role=role)
    user.set_unusable_password()
    user.save()
    if group:
        user.groups.add(create_groups()[group])
    return user


@pytest.fixture
def clinic(db):
    """Two specialities, three doctors (Meera has a login), four slots on 1 December 2026."""
    gm = Speciality.objects.create(name="General Medicine", slug="general-medicine")
    derm = Speciality.objects.create(name="Dermatology", slug="dermatology")
    meera = Doctor.objects.create(name="Dr. Meera Shah", speciality=gm, fee=500,
                                  user=make_user("drmeera", User.Role.DOCTOR, "Doctors"))
    arjun = Doctor.objects.create(name="Dr. Arjun Patel", speciality=gm, fee=600,
                                  user=make_user("drarjun", User.Role.DOCTOR, "Doctors"))
    kavya = Doctor.objects.create(name="Dr. Kavya Iyer", speciality=derm, fee=700)
    day = date(2026, 12, 1)
    slots = [TimeSlot.objects.create(doctor=d, date=day, start_time=t)
             for d, t in [(meera, time(10, 0)), (meera, time(10, 30)), (arjun, time(11, 0)), (kavya, time(12, 0))]]
    return {"meera": meera, "arjun": arjun, "kavya": kavya, "slots": slots}


@pytest.fixture
def asha(clinic):
    return Patient.objects.create(user=make_user("asha"), name="Asha Verma", phone="98250 11111")


@pytest.fixture
def ravi(clinic):
    return Patient.objects.create(user=make_user("ravi"), name="Ravi Kumar", phone="98250 22222")


@pytest.fixture
def reception(clinic):
    return make_user("reception", User.Role.ADMIN, "Reception")


@pytest.fixture
def booked(clinic, asha):
    """Asha's appointment in Dr. Meera Shah's 10:00 slot."""
    return Appointment.objects.create(slot=clinic["slots"][0], patient=asha, reason="Fever")


@pytest.fixture
def login(api):
    """login(user) -> the client, authenticated as user for every request (no password, no token)."""
    def as_user(user):
        api.force_authenticate(user=user)
        return api
    return as_user
