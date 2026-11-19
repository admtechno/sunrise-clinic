"""Module 9, Session 16: DATABASE_URL and the guard of the test settings."""
import subprocess
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings.database import database_from_url, describe

URL = "postgresql://clinic_app:s3cret%40word@ep-calm-sun-123456-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"  # not-a-secret


def test_every_part_of_the_address():
    db = database_from_url(URL)
    assert db["USER"] == "clinic_app"
    assert db["PASSWORD"] == "s3cret@word"            # %40 is an @
    assert db["HOST"] == "ep-calm-sun-123456-pooler.eu-central-1.aws.neon.tech"
    assert db["PORT"] == "5432"
    assert db["NAME"] == "neondb"
    assert db["OPTIONS"] == {"connect_timeout": 5, "sslmode": "require",
                             "channel_binding": "require"}


def test_describe_never_shows_the_password():
    text = describe(database_from_url(URL))
    assert "s3cret" not in text
    assert "password=11 characters" in text


@pytest.mark.parametrize("url", ["mysql://u:p@h/db", "postgresql://h/db", "postgresql://u:p@h/"])
def test_a_wrong_address_is_refused(url):
    with pytest.raises(ImproperlyConfigured):
        database_from_url(url)


@pytest.mark.parametrize("url", ["postgresql://u:firstpart/lastpart@h/db",     # a / not written %2F (not-a-secret)
                                 "postgresql://u:firstpart#lastpart@h/db",     # a # not written %23 (not-a-secret)
                                 "postgresql://u:firstpart@h:lastpart/db"])    # a port that is not a number (not-a-secret)
def test_a_broken_address_gives_a_hint_without_the_password(url):
    with pytest.raises(ImproperlyConfigured) as error:
        database_from_url(url)
    assert "%2F" in str(error.value)
    assert "firstpart" not in str(error.value) and "lastpart" not in str(error.value)


def test_the_tests_refuse_a_database_url():
    code = "import django, os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.test'; django.setup()"
    env = {"DATABASE_URL": URL, "DJANGO_SECRET_KEY": "x" * 50, "DB_NAME": "x", "DB_USER": "x",
           "PATH": "/usr/bin:/bin"}
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode == 1
    assert "Unset DATABASE_URL before running the tests." in result.stderr
