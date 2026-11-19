"""Run from the project folder: python setup_roles.py
Session 11: the clinic's groups and their permissions, a reception login and a login for Dr. Meera Shah.
Group = what a person may do (permissions). User.role = what a person is (Session 04).
No password is set here: set one with python manage.py changepassword drmeera (or reception)."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from django.contrib.auth.models import Group  # noqa: E402

from accounts.models import User  # noqa: E402
from clinic.models import Doctor  # noqa: E402
from clinic.roles import create_groups  # noqa: E402

for name, group in create_groups().items():      # Session 22: the groups now come from clinic/roles.py
    print(f"{name}: {group.permissions.count()} permissions")


def login(username, group, **defaults):
    user, created = User.objects.get_or_create(username=username, defaults=defaults)
    if created:
        user.set_unusable_password()      # no password until you set one
        user.save()
    user.groups.add(Group.objects.get(name=group))
    return user


reception = login("reception", "Reception", role=User.Role.ADMIN, is_staff=True)
print("reception | role:", reception.role, "| may add a slot:", reception.has_perm("clinic.add_timeslot"))
user = login("drmeera", "Doctors", role=User.Role.DOCTOR)
Doctor.objects.filter(name="Dr. Meera Shah").update(user=user)
user.refresh_from_db()
print("drmeera -> linked to", user.doctor.name, "| role:", user.role, "| may add a slot:", user.has_perm("clinic.add_timeslot"))
