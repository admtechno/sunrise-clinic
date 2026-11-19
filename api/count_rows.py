"""Run from the project folder: python count_rows.py
Module 9, Session 08: counts the rows of YOUR database (the one in .env), so that
you can compare them before and after a test run. It only reads."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from django.db import connection  # noqa: E402

from clinic.models import Appointment, Doctor, Report, TimeSlot  # noqa: E402

print(f"database {connection.settings_dict['NAME']}: "
      + ", ".join(f"{m._meta.verbose_name_plural} {m.objects.count()}"
                  for m in (Doctor, TimeSlot, Appointment, Report)))
