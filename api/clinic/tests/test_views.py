"""Session 13: pages, logins and permissions with pytest-django's test client."""
import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from clinic.services import book_slot

pytestmark = pytest.mark.django_db                   # every test in this file may use the database


def test_home_page(client):                         # no fixture with "db": the mark above allows the query
    response = client.get(reverse("clinic:home"))
    assert response.status_code == 200
    assert response.context["doctor_count"] == 0


def test_doctor_list_search(client, doctor):
    response = client.get(reverse("clinic:doctor_list"), {"q": "meera"})
    assert response.status_code == 200
    assert "Dr. Meera Shah" in response.text


def test_my_appointments_needs_login(client):
    response = client.get(reverse("clinic:my_appointments"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/my/appointments/"


def test_patient_cannot_cancel_someone_else(client, slot, asha, ravi):
    appointment = book_slot(slot, asha)
    client.force_login(ravi.user)
    response = client.post(reverse("clinic:cancel_appointment", args=[appointment.pk]))
    assert response.status_code == 404               # Session 10: no IDOR
    appointment.refresh_from_db()
    assert appointment.status == "booked"


@pytest.mark.parametrize("username, expected", [("ravi", 403), ("reception", 200)])
def test_slot_management_permission(client, django_user_model, username, expected):
    user = django_user_model.objects.create(username=username)
    if username == "reception":
        user.user_permissions.add(Permission.objects.get(codename="view_timeslot"))
    client.force_login(user)
    assert client.get(reverse("clinic:slot_list")).status_code == expected


def test_doctor_list_query_count(client, doctor, django_assert_num_queries):
    with django_assert_num_queries(3):     # count for the pages, doctors with their speciality, specialities
        client.get(reverse("clinic:doctor_list"))
