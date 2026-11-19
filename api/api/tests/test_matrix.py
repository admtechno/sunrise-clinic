"""Module 9, Session 09: who may do what with the endpoints that the Clinic Desk uses,
as ONE table. Each cell is one test; its id says the row and the person, for example
test_matrix[reports POST-drmeera-403]. The people: anon (not logged in), asha (the
patient of the appointment), ravi (another patient), drmeera (the slot's doctor),
drarjun (another doctor) and reception."""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User

from .factories import (AppointmentFactory, PatientFactory, UserFactory,
                        doctor_with_login)

PEOPLE = ["anon", "asha", "ravi", "drmeera", "drarjun", "reception"]
PDF = b"%PDF-1.4\n% a tiny test file\n"

#      row               anon asha ravi drmeera drarjun reception
MATRIX = {
    "appointment GET":  [401, 200, 404, 200, 200, 200],  # drarjun? mini challenge
    "reports GET":      [401, 200, 404, 200, 403, 403],
    "reports POST":     [401, 201, 404, 403, 403, 403],
    "cancel POST":      [401, 200, 404, 403, 403, 200],
    "me GET":           [401, 200, 200, 200, 200, 200],
}


@pytest.fixture
def world(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path                # uploads go to a temporary folder
    meera = doctor_with_login("drmeera", name="Dr. Meera Shah")
    doctor_with_login("drarjun", name="Dr. Arjun Patel")
    asha = PatientFactory(user=UserFactory(username="asha"), name="Asha Verma")
    PatientFactory(user=UserFactory(username="ravi"), name="Ravi Kumar")
    UserFactory(username="reception", role=User.Role.ADMIN, group="Reception")
    return AppointmentFactory(slot__doctor=meera, patient=asha)


def send(api, row, appointment):
    a = f"/api/v1/appointments/{appointment.pk}"
    if row == "reports POST":
        upload = {"file": SimpleUploadedFile("scan.pdf", PDF)}
        return api.post(f"{a}/reports/", upload, format="multipart")
    path = {"appointment GET": f"{a}/", "reports GET": f"{a}/reports/",
            "cancel POST": f"{a}/cancel/", "me GET": "/api/v1/me/"}[row]
    return api.post(path) if row.endswith("POST") else api.get(path)


CELLS = [pytest.param(row, who, code, id=f"{row}-{who}-{code}")
         for row, codes in MATRIX.items() for who, code in zip(PEOPLE, codes)]


@pytest.mark.parametrize("row, who, expected", CELLS)
def test_matrix(api, world, row, who, expected):
    if who != "anon":
        api.force_authenticate(user=User.objects.get(username=who))
    assert send(api, row, world).status_code == expected
