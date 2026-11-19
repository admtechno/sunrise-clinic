"""Module 9, Session 09: the answers the Clinic Desk reads keep the promise of the
OpenAPI schema. One test per screen's request, and the error shape for each kind
of error."""
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile

from .contract import check_contract
from .factories import AppointmentFactory, SlotFactory

A = "/api/v1/appointments"


@pytest.fixture
def booked(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    appointment = AppointmentFactory()
    SlotFactory(doctor=appointment.slot.doctor)   # a free slot of the same doctor
    SlotFactory.create_batch(2)                   # and two of other doctors
    return appointment


def test_the_schema_has_no_errors_or_warnings():
    call_command("spectacular", "--validate", "--fail-on-warn", stdout=StringIO())


@pytest.mark.parametrize("path", [
    "/api/v1/doctors/", "/api/v1/doctors/?page_size=1&ordering=-fee",
    "/api/v1/specialities/", "/api/v1/slots/?free=true", "/api/v1/stats/"])
def test_public_answers(api, booked, path):
    check_contract(api.get(path))


@pytest.mark.parametrize("path", [
    "/me/", "/appointments/", "/appointments/{a}/", "/appointments/{a}/reports/",
    "/doctors/{d}/", "/doctors/{d}/slots/"])
def test_what_a_patient_reads(api, booked, path):
    api.force_authenticate(user=booked.patient.user)
    path = path.format(a=booked.pk, d=booked.slot.doctor.pk)
    check_contract(api.get("/api/v1" + path))


def test_what_a_patient_sends(api, booked):
    api.force_authenticate(user=booked.patient.user)
    upload = {"file": SimpleUploadedFile("scan.pdf", b"%PDF-1.4\n")}
    check_contract(api.post(f"{A}/{booked.pk}/reports/", upload, format="multipart"))
    check_contract(api.post(f"{A}/{booked.pk}/cancel/"))


@pytest.mark.parametrize("make", ["401", "404", "400", "409", "403"])
def test_every_kind_of_error_has_the_error_shape(api, booked, make):
    if make != "401":
        api.force_authenticate(user=booked.patient.user)
    response = {
        "401": lambda: api.get("/api/v1/me/"),
        "404": lambda: api.get(f"{A}/999999/"),
        "400": lambda: api.post(f"{A}/", {"slot": booked.slot.pk}, format="json"),
        "409": lambda: (api.post(f"{A}/{booked.pk}/cancel/"),
                        api.post(f"{A}/{booked.pk}/cancel/"))[1],
        "403": lambda: api.post("/api/v1/slots/", {}, format="json"),
    }[make]()
    assert str(response.status_code) == make
    check_contract(response)
