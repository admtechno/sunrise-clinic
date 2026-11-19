"""Settings for automated tests (Session 13): fast, quiet, and with their own upload folder."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, LOGGING

# Module 9, Session 16: tests never run against an address from the environment:
# they would create and delete tables on whatever database it names.
if os.environ.get("DATABASE_URL"):
    raise ImproperlyConfigured("Unset DATABASE_URL before running the tests.")

DEBUG = False
ALLOWED_HOSTS = ["testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]   # fast; NEVER outside tests
MEDIA_ROOT = BASE_DIR / "test_media"
LOGGING = {**LOGGING, "loggers": {"clinic": {"handlers": ["console"], "level": "WARNING"}}}
