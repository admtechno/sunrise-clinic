"""Run from the api folder: python lab_logins.py
Module 9 lab helper: the logins the Clinic Desk uses. It runs setup_roles.py (reception and drmeera) and adds
the patient logins asha and ravi, linked to the patients Asha Verma and Ravi Kumar of the sample data.
No password is set: give each login one you invent with python manage.py changepassword asha (ravi, reception)."""
import os
import runpy

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from accounts.models import User  # noqa: E402
from clinic.models import Patient  # noqa: E402

runpy.run_path("setup_roles.py")
for username, name in [("asha", "Asha Verma"), ("ravi", "Ravi Kumar")]:
    user, created = User.objects.get_or_create(username=username, defaults={"role": User.Role.PATIENT})
    if created:
        user.set_unusable_password()
        user.save()
    Patient.objects.filter(name=name).update(user=user)
    print(f"{username} -> patient {Patient.objects.get(user=user).name} | password set: {user.has_usable_password()}")
