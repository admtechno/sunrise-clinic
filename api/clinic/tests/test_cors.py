"""Session 21: the API answers the React origin, and nobody else."""
import pytest

REACT = "http://localhost:5173"


@pytest.fixture
def cors(settings):                              # the allow list for these tests, whatever .env says
    settings.CORS_ALLOWED_ORIGINS = [REACT]


def test_allowed_origin_gets_the_header(client, cors, doctor):
    response = client.get("/api/v1/doctors/", headers={"Origin": REACT})
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == REACT


def test_other_origin_gets_no_header(client, cors, doctor):
    response = client.get("/api/v1/doctors/", headers={"Origin": "http://attacker.example"})
    assert response.status_code == 200          # the server still answers: CORS is enforced by the browser
    assert "Access-Control-Allow-Origin" not in response


def test_preflight_allows_the_token_header(client, cors):
    response = client.options("/api/v1/appointments/", headers={
        "Origin": REACT, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization, content-type"})
    assert response.status_code == 200
    assert "authorization" in response["Access-Control-Allow-Headers"]
    assert "POST" in response["Access-Control-Allow-Methods"]


def test_website_pages_get_no_cors_header(client, cors, doctor):
    response = client.get("/", headers={"Origin": REACT})   # CORS_URLS_REGEX: only /api/
    assert "Access-Control-Allow-Origin" not in response
