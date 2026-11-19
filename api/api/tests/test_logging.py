"""Module 9, Session 20: what the log on the host must show."""
import logging
import runpy
from pathlib import Path

import pytest
from django.test import Client

GUNICORN_CONF = Path(__file__).resolve().parents[2] / "gunicorn.conf.py"


def test_each_request_line_shows_its_time_in_ms():
    conf = runpy.run_path(str(GUNICORN_CONF))
    assert conf["accesslog"] == "-"
    assert "%(s)s" in conf["access_log_format"]          # the status
    assert "%(M)sms" in conf["access_log_format"]        # how long it took


@pytest.mark.django_db
def test_a_500_is_logged_with_its_traceback(monkeypatch):
    def broken(self, request, *args, **kwargs):
        raise RuntimeError("a bug in a view")
    monkeypatch.setattr("api.views.DoctorViewSet.list", broken)
    seen = []
    handler = logging.Handler()
    handler.emit = seen.append
    logging.getLogger("django.request").addHandler(handler)
    try:
        response = Client(raise_request_exception=False).get("/api/v1/doctors/")
    finally:
        logging.getLogger("django.request").removeHandler(handler)
    assert response.status_code == 500
    assert seen and seen[0].exc_info[0] is RuntimeError
