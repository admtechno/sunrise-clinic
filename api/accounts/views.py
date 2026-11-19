from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import redirect, render

from clinic.models import Patient

from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():                  # the user and the patient record, or neither
                user = form.save()                      # role is "patient" by default (Session 04)
                patient, _ = Patient.objects.get_or_create(phone=form.cleaned_data["phone"],
                                                           defaults={"name": form.cleaned_data["name"]})
                if patient.user_id is None:             # link a desk-registered patient to the new login
                    patient.user = user
                    patient.save(update_fields=["user"])
            login(request, user)                        # signed in straight away
            return redirect("clinic:my_appointments")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})
