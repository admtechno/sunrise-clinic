"""Module 9, Session 14: /health/ and /ready/."""
import pytest
from django.db.utils import OperationalError


def test_health_answers_without_the_database(client):
    # no django_db mark: pytest-django refuses any database use in this test
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "local"}
    assert "no-cache" in response["Cache-Control"]


@pytest.mark.django_db
def test_ready_asks_the_database(client):
    response = client.get("/ready/")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


@pytest.mark.django_db
def test_ready_says_503_and_no_details_when_the_database_fails(client, monkeypatch):
    def broken(self, sql, params=None):
        raise OperationalError("connection to server at 10.0.0.5 failed: secret detail")
    monkeypatch.setattr("django.db.backends.utils.CursorWrapper.execute", broken)
    response = client.get("/ready/")
    assert response.status_code == 503
    assert response.json() == {"status": "not ready", "database": "unavailable"}
    assert b"10.0.0.5" not in response.content


@pytest.mark.parametrize("address", ["/health/", "/ready/"])
def test_only_get_and_head(client, address):
    assert client.post(address).status_code == 405


def test_health_names_the_deployed_commit(client, monkeypatch):
    # Module 9, Session 17: Render sets RENDER_GIT_COMMIT (40 hex characters)
    monkeypatch.setenv("RENDER_GIT_COMMIT", "3f9c2a1b7d" + "0" * 30)
    assert client.get("/health/").json()["version"] == "3f9c2a1"
