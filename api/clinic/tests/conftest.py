"""Session 13: fixtures shared by every test in clinic/tests/. pytest finds them by name."""
from datetime import date, time

import pytest

from clinic.models import Doctor, Patient, Speciality, TimeSlot


@pytest.fixture
def doctor(db):                                  # "db": this fixture may use the test database
    speciality = Speciality.objects.create(name="General Medicine", slug="general-medicine")
    return Doctor.objects.create(name="Dr. Meera Shah", speciality=speciality, fee=500)


@pytest.fixture
def slot(doctor):                                # fixtures can use other fixtures
    return TimeSlot.objects.create(doctor=doctor, date=date(2026, 12, 1), start_time=time(10, 0))


@pytest.fixture
def asha(db, django_user_model):                 # a patient login, no password needed
    user = django_user_model.objects.create(username="asha")
    return Patient.objects.create(user=user, name="Asha Verma", phone="98250 11111")


@pytest.fixture
def ravi(db, django_user_model):
    user = django_user_model.objects.create(username="ravi")
    return Patient.objects.create(user=user, name="Ravi Kumar", phone="98250 22222")


@pytest.fixture
def asha_client(client, asha):                   # "client" is pytest-django's test client
    client.force_login(asha.user)
    return client


@pytest.fixture
def media(settings, tmp_path):                   # uploads go to a fresh temporary folder per test
    settings.MEDIA_ROOT = tmp_path
    return tmp_path
