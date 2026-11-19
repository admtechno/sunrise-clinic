"""Module 9, Session 12: reset_test_data refuses where it could delete real data."""
import secrets

import pytest
from django.core.management import CommandError, call_command

from accounts.models import User
from clinic.management.commands import reset_test_data
from clinic.models import Appointment


def test_it_refuses_without_the_e2e_settings():
    with pytest.raises(CommandError, match="runs only with config.settings.e2e"):
        call_command("reset_test_data")


def test_it_refuses_a_database_that_does_not_end_in_e2e(settings):
    settings.E2E = True
    with pytest.raises(CommandError, match="does not end in _e2e"):
        call_command("reset_test_data")   # pytest's database: test_<DB_NAME>


@pytest.mark.django_db(transaction=True)   # flush needs a real transaction
def test_it_loads_the_sample_data_and_four_logins(settings, monkeypatch, capsys):
    settings.E2E = True
    monkeypatch.setattr(reset_test_data, "database_name", lambda: "m9_e2e")
    password = secrets.token_hex(8)   # made new for each run
    monkeypatch.setenv("E2E_PASSWORD", password)
    User.objects.create_user("leftover")          # something the reset must remove
    call_command("reset_test_data")
    assert not User.objects.filter(username="leftover").exists()
    assert Appointment.objects.count() == 2       # the two of clinic_s06
    asha = User.objects.get(username="asha")
    assert asha.check_password(password) and asha.patient.name == "Asha Verma"
    assert User.objects.get(username="drmeera").doctor.name == "Dr. Meera Shah"
    assert password not in capsys.readouterr().out   # the password is never printed
