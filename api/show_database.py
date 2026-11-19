"""Module 9, Session 16: which database Django will use, without the password.
    python show_database.py     (in api; reads .env and DATABASE_URL)
Safe in a shared terminal: the password is shown only as its length."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from django.conf import settings  # noqa: E402

from config.settings.database import describe  # noqa: E402

db = settings.DATABASES["default"]
if os.environ.get("DATABASE_URL"):
    print("from DATABASE_URL")
else:
    print("from DB_NAME, DB_USER, ... (.env)")
print(describe(db))
print(f"CONN_MAX_AGE={db['CONN_MAX_AGE']} "
      f"DISABLE_SERVER_SIDE_CURSORS={db['DISABLE_SERVER_SIDE_CURSORS']}")
