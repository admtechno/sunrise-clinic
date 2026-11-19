"""Session 22: who may do what, as one table. Each row is one test (pytest.mark.parametrize)."""
import pytest

from clinic.models import Appointment

A = "/api/v1/appointments"


def user_for(who, request):
    """'anon' -> None; otherwise the login of a fixture: asha, ravi, reception, drmeera, drarjun."""
    if who == "anon":
        return None
    clinic = request.getfixturevalue("clinic")
    if who in ("drmeera", "drarjun"):
        return clinic[who[2:]].user
    found = request.getfixturevalue(who)
    return getattr(found, "user", found)          # a Patient has .user; reception is already a User


@pytest.mark.parametrize("who, expected", [
    ("anon", 401), ("asha", 201), ("drmeera", 403), ("reception", 403)])
def test_who_can_book(api, request, clinic, asha, who, expected):
    api.force_authenticate(user=user_for(who, request))
    response = api.post(f"{A}/", {"slot": clinic["slots"][1].pk}, format="json")
    assert response.status_code == expected


@pytest.mark.parametrize("who, expected", [
    ("anon", 401), ("ravi", 404), ("drmeera", 403), ("asha", 200), ("reception", 200)])
def test_who_can_cancel_ashas_appointment(api, request, booked, who, expected):
    api.force_authenticate(user=user_for(who, request))
    response = api.post(f"{A}/{booked.pk}/cancel/")
    assert response.status_code == expected
    booked.refresh_from_db()
    assert booked.status == ("cancelled" if expected == 200 else "booked")


@pytest.mark.parametrize("who, expected", [
    ("asha", 403), ("drarjun", 403), ("drmeera", 200)])
def test_only_the_slots_doctor_can_complete(api, request, booked, who, expected):
    api.force_authenticate(user=user_for(who, request))
    assert api.post(f"{A}/{booked.pk}/complete/").status_code == expected


@pytest.mark.parametrize("who, expected", [
    ("anon", 401), ("asha", 403), ("reception", 403), ("drmeera", 200)])
def test_doctor_schedule(api, request, booked, who, expected):
    api.force_authenticate(user=user_for(who, request))
    assert api.get("/api/v1/doctor/schedule/").status_code == expected


@pytest.mark.parametrize("who, expected", [
    ("anon", 401), ("asha", 403), ("drmeera", 403), ("reception", 201)])
def test_who_can_add_a_slot(api, request, clinic, who, expected):
    api.force_authenticate(user=user_for(who, request))
    data = {"doctor": clinic["kavya"].pk, "date": "2026-12-02", "start_time": "09:00"}
    assert api.post("/api/v1/slots/", data, format="json").status_code == expected


def test_patients_see_only_their_own(login, booked, ravi, clinic):
    Appointment.objects.create(slot=clinic["slots"][2], patient=ravi)
    mine = login(ravi.user).get(f"{A}/").json()
    assert [a["patient"] for a in mine["results"]] == ["Ravi Kumar"]


def test_no_double_booking_through_the_api(login, booked, ravi):
    response = login(ravi.user).post(f"{A}/", {"slot": booked.slot.pk}, format="json")
    assert response.status_code == 400
    assert response.json()["error"]["fields"] == {"slot": ["This time slot is already booked."]}


def test_booking_answer(login, asha, clinic):
    response = login(asha.user).post(f"{A}/", {"slot": clinic["slots"][1].pk, "reason": " Cough "}, format="json")
    body = response.json()
    assert body["slot"] == {"id": clinic["slots"][1].pk, "doctor": "Dr. Meera Shah",
                            "date": "2026-12-01", "start_time": "10:30"}
    assert (body["patient"], body["status"], body["reason"]) == ("Asha Verma", "booked", "Cough")
    assert "created_at" in body                  # the value changes every run: check that it is there only
