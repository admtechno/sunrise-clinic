"""Module 9, Session 07: the report upload of the API.
The files are made in memory; MEDIA_ROOT is a temporary folder for each test."""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from clinic.models import Report

A = "/api/v1/appointments"
PDF = b"%PDF-1.4\n% a tiny test file\n"


@pytest.fixture(autouse=True)
def media_in_tmp(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path  # no test writes into the real media folder


def upload(name, data):
    return {"file": SimpleUploadedFile(name, data)}


def test_the_patient_uploads_a_pdf(login, booked):
    api = login(booked.patient.user)
    response = api.post(f"{A}/{booked.pk}/reports/",
                        upload("blood_test.pdf", PDF), format="multipart")
    assert response.status_code == 201
    assert response.json()["original_name"] == "blood_test.pdf"
    assert "file" not in response.json()  # the stored path stays private
    assert Report.objects.get().size == len(PDF)


@pytest.mark.parametrize("name, data, message", [
    ("notes.txt", b"hello", "File extension"),
    ("not_really.pdf", b"<html></html>", "not a real PDF file"),
    ("big_scan.pdf", PDF + b"0" * (2 * 1024 * 1024), "the limit is 2.0"),
])
def test_bad_files_are_refused(login, booked, name, data, message):
    api = login(booked.patient.user)
    response = api.post(f"{A}/{booked.pk}/reports/",
                        upload(name, data), format="multipart")
    assert response.status_code == 400
    assert message in response.json()["error"]["fields"]["file"][0]
    assert Report.objects.count() == 0


def test_no_file_is_a_field_error(login, booked):
    api = login(booked.patient.user)
    response = api.post(f"{A}/{booked.pk}/reports/", {}, format="multipart")
    assert response.status_code == 400
    assert response.json()["error"]["fields"]["file"] == ["No file was submitted."]


def test_json_is_not_accepted(login, booked):
    api = login(booked.patient.user)
    response = api.post(f"{A}/{booked.pk}/reports/", {"file": "x"}, format="json")
    assert response.status_code == 415


@pytest.mark.parametrize("who, read, write", [
    ("anon", 401, 401), ("ravi", 404, 404), ("drmeera", 200, 403),
    ("drarjun", 403, 403), ("reception", 403, 403)])
def test_who_may_read_and_upload(api, request, booked, who, read, write):
    from api.tests.test_roles import user_for
    api.force_authenticate(user=user_for(who, request))
    assert api.get(f"{A}/{booked.pk}/reports/").status_code == read
    response = api.post(f"{A}/{booked.pk}/reports/",
                        upload("a.pdf", PDF), format="multipart")
    assert response.status_code == write
