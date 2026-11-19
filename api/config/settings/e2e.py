"""Settings for the browser tests (Module 9, Session 12).
Use them with DJANGO_SETTINGS_MODULE=config.settings.e2e. The database is a
database of its own, whose name must end in _e2e, because reset_test_data
deletes everything in it before each test."""
import os

from django.core.exceptions import ImproperlyConfigured

from .dev import *  # noqa: F401,F403
from .dev import DATABASES, REST_FRAMEWORK

# Module 9, Session 16: tests never run against an address from the environment:
# they would create and delete tables on whatever database it names.
if os.environ.get("DATABASE_URL"):
    raise ImproperlyConfigured("Unset DATABASE_URL before running the tests.")
E2E = True  # reset_test_data runs only when this is True
DATABASES["default"]["NAME"] = os.environ.get("E2E_DB_NAME", "m9_e2e")
if not DATABASES["default"]["NAME"].endswith("_e2e"):
    raise ImproperlyConfigured("The browser tests need a database ending in _e2e.")
# every test logs in again: the limit of 5 logins a minute would stop them
RATES = {**REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"], "login": "1000/minute"}
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": RATES}
