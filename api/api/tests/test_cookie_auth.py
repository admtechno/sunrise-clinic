"""Module 9, Session 05: the cookie login.

The password is random for each test run (secrets), so no file holds one."""
import secrets

import pytest

from api.views_cookie import COOKIE, COOKIE_PATH

H = {"HTTP_X_CLINIC_CLIENT": "desk"}  # the header every cookie request needs
LOGIN, REFRESH = "/api/v1/auth/cookie/login/", "/api/v1/auth/cookie/refresh/"
LOGOUT = "/api/v1/auth/cookie/logout/"


@pytest.fixture
def password(asha):
    value = secrets.token_hex(8)
    asha.user.set_password(value)
    asha.user.save()
    return value


def cookie_login(api, password):
    body = {"username": "asha", "password": password}
    return api.post(LOGIN, body, format="json", **H)


def test_login_sets_an_httponly_cookie_and_returns_only_access(api, password):
    r = cookie_login(api, password)
    assert r.status_code == 200 and list(r.json()) == ["access"]
    cookie = r.cookies[COOKIE]
    assert cookie["httponly"] and cookie["path"] == COOKIE_PATH
    assert cookie["samesite"] == "Lax"


def test_without_the_header_the_cookie_views_refuse(api, password):
    body = {"username": "asha", "password": password}
    r = api.post(LOGIN, body, format="json")  # no header
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "permission_denied"


def test_wrong_password(api, password):
    r = cookie_login(api, password + "x")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "no_active_account"


def test_refresh_works_once(api, password):
    cookie_login(api, password)
    old = api.cookies[COOKIE].value
    r = api.post(REFRESH, **H)
    assert r.status_code == 200 and "access" in r.json()
    assert api.cookies[COOKIE].value != old  # a new refresh token
    api.cookies[COOKIE] = old  # someone replays the old cookie
    r = api.post(REFRESH, **H)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "token_not_valid"


def test_refresh_without_a_cookie(api, db):
    r = api.post(REFRESH, **H)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


def test_logout_ends_the_refresh_token(api, password):
    cookie_login(api, password)
    old = api.cookies[COOKIE].value
    r = api.post(LOGOUT, **H)
    assert r.status_code == 204 and r.cookies[COOKIE]["max-age"] == 0
    api.cookies[COOKIE] = old  # the token in it is on the blacklist now
    assert api.post(REFRESH, **H).status_code == 401


def test_the_access_token_works_on_the_api(api, password):
    access = cookie_login(api, password).json()["access"]
    r = api.get("/api/v1/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert r.status_code == 200 and r.json()["username"] == "asha"
