"""Module 9, Session 09: rules that depend on the clock, tested with time-machine.
travel() sets "now" for the code under test (tick=False: the clock stands still);
traveller.shift() moves it. Nobody waits five real minutes, and the result is the
same on every day of the year."""
import secrets
from datetime import UTC, date, datetime, timedelta
from io import StringIO

import pytest
import time_machine
from django.core.management import call_command

from clinic.models import TimeSlot

from .factories import DoctorFactory, PatientFactory, UserFactory

TOKEN, ME = "/api/v1/auth/token/", "/api/v1/me/"


def at(text):                                      # "2026-12-01 10:00" in UTC
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


@pytest.fixture
def password(db):
    value = secrets.token_urlsafe(12)             # random for each run, never printed
    PatientFactory(user=UserFactory(username="asha", password=value))
    return value


@time_machine.travel(at("2026-12-03 09:00"), tick=False)   # a Thursday
def test_next_week_starts_on_the_next_monday(db):
    DoctorFactory(name="Dr. Meera Shah")
    out = StringIO()
    call_command("create_next_week_slots", stdout=out)
    days = sorted(set(TimeSlot.objects.values_list("date", flat=True)))
    assert days[0] == date(2026, 12, 7) and days[-1] == date(2026, 12, 11)
    assert "20 slots created for 07 Dec to 11 Dec 2026." in out.getvalue()


@pytest.mark.parametrize("today, monday", [
    ("2026-12-06", date(2026, 12, 7)),            # a Sunday: tomorrow
    ("2026-12-07", date(2026, 12, 14)),           # a Monday: in seven days, not today
])
def test_the_next_monday_from_a_sunday_and_a_monday(db, today, monday):
    DoctorFactory()
    with time_machine.travel(at(today + " 09:00"), tick=False):
        call_command("create_next_week_slots", stdout=StringIO())
    assert TimeSlot.objects.order_by("date").first().date == monday


def test_the_access_token_lives_five_minutes(api, password):
    with time_machine.travel(at("2026-12-01 10:00"), tick=False) as clock:
        login = {"username": "asha", "password": password}
        access = api.post(TOKEN, login, format="json").json()["access"]
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        clock.shift(timedelta(minutes=4, seconds=59))
        assert api.get(ME).status_code == 200    # 10:04:59, still valid
        clock.shift(timedelta(seconds=2))
        response = api.get(ME)                    # 10:05:01, expired
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "token_not_valid"


def test_the_login_limit_ends_after_a_minute(api, password):
    wrong = {"username": "asha", "password": "not-" + password}
    with time_machine.travel(at("2026-12-01 10:00"), tick=False) as clock:
        for _ in range(5):                        # login: 5 a minute
            api.post(TOKEN, wrong, format="json")
        assert api.post(TOKEN, wrong, format="json").status_code == 429
        clock.shift(timedelta(seconds=61))
        right = {"username": "asha", "password": password}
        assert api.post(TOKEN, right, format="json").status_code == 200
