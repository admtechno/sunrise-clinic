"""Module 9, Session 08: a test owns its data. pytest-django makes a test database
next to yours (test_ + its name); the rows of each test are rolled back at its end."""
from django.db import connection

from clinic.models import Appointment


def test_tests_use_their_own_database(db):
    name = connection.settings_dict["NAME"]
    print(f"\ntest database: {name}")              # shown with python -m pytest -s
    assert name.startswith("test_")                # never the database of the lab


def test_a_test_starts_with_no_appointments(db):
    assert Appointment.objects.count() == 0       # your sample data is not here
