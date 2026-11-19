from django import forms
from django.contrib.auth.forms import UserCreationForm

from clinic.forms import BookingForm

from .models import User


class SignUpForm(UserCreationForm):
    """A patient account: username and password (checked by AUTH_PASSWORD_VALIDATORS) plus the patient details."""
    name = forms.CharField(max_length=100, label="Full name")
    phone = forms.CharField(max_length=15, label="Mobile number", help_text="10 digits")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email"]

    clean_phone = BookingForm.clean_phone          # the same phone rule as the booking form
