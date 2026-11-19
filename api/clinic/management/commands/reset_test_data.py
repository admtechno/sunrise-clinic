"""python manage.py reset_test_data (Module 9, Session 12)
Empties the browser-test database and loads the sample data again, with four
logins (asha, ravi, drmeera, reception) whose password comes from the
environment variable E2E_PASSWORD. It refuses to run unless the settings say
E2E = True and the database name ends in _e2e: it never empties your own data."""
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from accounts.models import User
from clinic.models import Doctor, Patient
from clinic.roles import create_groups

FIXTURES = ["clinic_seed", "clinic_more", "clinic_s06"]
LOGINS = [  # username, role, group, linked to
    ("asha", User.Role.PATIENT, None, ("patient", "Asha Verma")),
    ("ravi", User.Role.PATIENT, None, ("patient", "Ravi Kumar")),
    ("drmeera", User.Role.DOCTOR, "Doctors", ("doctor", "Dr. Meera Shah")),
    ("reception", User.Role.ADMIN, "Reception", None),
]


def database_name():
    return connection.settings_dict["NAME"]


class Command(BaseCommand):
    help = "Empty the browser-test database; load the sample data and 4 logins."

    def handle(self, *args, **options):
        if not getattr(settings, "E2E", False):
            raise CommandError(
                "reset_test_data runs only with config.settings.e2e "
                f"(it would delete everything in {database_name()}).")
        if not database_name().endswith("_e2e"):
            raise CommandError(
                f"The database {database_name()} does not end in _e2e.")
        password = os.environ.get("E2E_PASSWORD", "")
        if len(password) < 12:
            raise CommandError(
                "Set E2E_PASSWORD (12 characters or more) for the test logins.")

        call_command("flush", interactive=False, verbosity=0)
        call_command("loaddata", *FIXTURES, verbosity=0)
        create_groups()
        for username, role, group, link in LOGINS:
            user = User.objects.create_user(
                username, password=password, role=role,
                is_staff=role == User.Role.ADMIN)
            if group:
                user.groups.add(Group.objects.get(name=group))
            if link and link[0] == "patient":
                Patient.objects.filter(name=link[1]).update(user=user)
            if link and link[0] == "doctor":
                Doctor.objects.filter(name=link[1]).update(user=user)
        names = ", ".join(name for name, *_ in LOGINS)
        self.stdout.write(f"{database_name()}: sample data loaded, logins {names}"
                          " (password from E2E_PASSWORD)")
