"""Module 9, Session 09: tests written from the coverage report. Each one checks a
rule whose lines no test had run (python -m pytest --cov=api --cov-report=...)."""
import pytest

from accounts.models import User
from api.views_cookie import COOKIE

from .factories import DoctorFactory, UserFactory


@pytest.fixture
def reception(db):
    return UserFactory(username="reception", role=User.Role.ADMIN, group="Reception")


def test_a_fee_of_zero_is_refused(api, db):         # serializers.py 29-31
    api.force_authenticate(user=UserFactory(username="boss", is_superuser=True))
    doctor = DoctorFactory()
    response = api.patch(f"/api/v1/doctors/{doctor.pk}/", {"fee": "0"}, format="json")
    assert response.status_code == 400
    fields = response.json()["error"]["fields"]
    assert fields == {"fee": ["The fee must be more than zero."]}


@pytest.mark.parametrize("start, message", [       # serializers.py 68, 74
    ("10:15", "Slots start on the hour or at half past."),
    ("07:00", "The clinic is open from 08:00 to 20:00."),
])
def test_slot_times_follow_the_clinic_hours(api, reception, start, message):
    api.force_authenticate(user=reception)
    data = {"doctor": DoctorFactory().pk, "date": "2026-12-02", "start_time": start}
    response = api.post("/api/v1/slots/", data, format="json")
    assert response.status_code == 400
    assert response.json()["error"]["fields"]["start_time"] == [message]


def test_logout_with_a_broken_cookie_still_logs_out(api, db):  # cookie 110-111
    api.cookies[COOKIE] = "not-a-token"
    response = api.post("/api/v1/auth/cookie/logout/", HTTP_X_CLINIC_CLIENT="desk")
    assert response.status_code == 204
    assert response.cookies[COOKIE].value == ""   # the cookie is removed
