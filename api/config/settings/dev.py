"""Settings for your own PC: python manage.py runserver uses these (see manage.py)."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
