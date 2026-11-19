"""Session 13: the report upload checks (Session 12) with files made in memory."""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from clinic.models import Report
from clinic.services import book_slot

PDF = b"%PDF-1.4\n% a tiny test file\n"


@pytest.fixture
def appointment(slot, asha):
    return book_slot(slot, asha)


@pytest.mark.parametrize("name, content, error", [
    ("scan.pdf", PDF, None),
    ("scan.pdf", b"<html>not a pdf</html>", "not a real PDF file"),
    ("tool.exe", b"MZ", "is not allowed"),
    ("big.pdf", PDF + b"0" * (2 * 1024 * 1024), "the limit is"),
], ids=["good pdf", "fake pdf", "exe", "too big"])
def test_upload_checks(asha_client, appointment, media, name, content, error):
    upload = SimpleUploadedFile(name, content)
    response = asha_client.post(f"/my/appointments/{appointment.pk}/reports/", {"file": upload})
    if error is None:
        assert response.status_code == 302
        report = Report.objects.get()
        assert report.original_name == name
        assert (media / report.file.name).exists()           # stored in the temporary folder
    else:
        assert error in response.text
        assert not Report.objects.exists()
