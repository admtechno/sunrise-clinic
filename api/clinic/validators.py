"""Session 12: checks for uploaded patient reports. Never trust the file name: check the size
and the first bytes of the content as well."""
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

REPORT_TYPES = ["pdf", "jpg", "jpeg", "png"]
SIGNATURES = {                      # the first bytes of each file type ("magic numbers")
    ".pdf": b"%PDF-",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
}


def validate_report_size(file):
    if file.size > settings.REPORT_MAX_BYTES:
        raise ValidationError("The file is %(size)s; the limit is %(limit)s.", code="too_big",
                              params={"size": filesizeformat(file.size), "limit": filesizeformat(settings.REPORT_MAX_BYTES)})


def validate_report_content(file):
    signature = SIGNATURES.get(Path(file.name).suffix.lower())
    if signature is None:
        return                      # unknown extension: FileExtensionValidator reports it
    start = file.read(len(signature))
    file.seek(0)                    # rewind, so the file is saved from the beginning
    if start != signature:
        raise ValidationError("The content of this file is not a real %(ext)s file.", code="bad_content",
                              params={"ext": Path(file.name).suffix.lower()[1:].upper()})
