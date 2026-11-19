"""Session 22: authentication in tests. Most tests use force_authenticate; these test the real JWT login."""
import secrets
from datetime import timedelta

import pytest
from rest_framework_simplejwt.tokens import AccessToken

ME = "/api/v1/me/"


@pytest.fixture
def password(asha):
    """A random password for asha, made inside the test run and never printed."""
    value = secrets.token_urlsafe(18)
    asha.user.set_password(value)
    asha.user.save()
    return value


def test_me_needs_a_login(api):
    response = api.get(ME)
    assert response.status_code == 401
    assert response["WWW-Authenticate"].startswith("Bearer")


def test_force_authenticate(api, asha):
    api.force_authenticate(user=asha.user)
    assert api.get(ME).json()["username"] == "asha"


def test_real_jwt_login(api, asha, password):
    response = api.post("/api/v1/auth/token/", {"username": "asha", "password": password}, format="json")
    assert response.status_code == 200
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")   # every request from now on
    me = api.get(ME).json()
    assert me["username"] == "asha" and me["authenticated_by"] == "JWTAuthentication"


def test_wrong_password_is_401(api, asha, password):
    response = api.post("/api/v1/auth/token/", {"username": "asha", "password": "not-" + password}, format="json")
    assert response.status_code == 401


def test_expired_token_is_refused(api, asha):
    token = AccessToken.for_user(asha.user)
    token.set_exp(lifetime=-timedelta(minutes=1))   # expired a minute ago
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api.get(ME)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_not_valid"


def test_changed_token_is_refused(api, asha):
    head, body, signature = str(AccessToken.for_user(asha.user)).split(".")
    changed = body[:-2] + ("A" if body[-2] != "A" else "B") + body[-1]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {head}.{changed}.{signature}")
    assert api.get(ME).status_code == 401


def test_login_is_throttled(api, asha):
    for _ in range(5):                              # login: 5/minute (Session 19)
        api.post("/api/v1/auth/token/", {"username": "asha", "password": secrets.token_urlsafe(12)}, format="json")
    response = api.post("/api/v1/auth/token/", {"username": "asha", "password": "x"}, format="json")
    assert response.status_code == 429
    assert 1 <= int(response["Retry-After"]) <= 60
