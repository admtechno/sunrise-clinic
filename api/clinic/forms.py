from datetime import date, time

from django import forms

from .models import Doctor, Patient, Report, TimeSlot
from .services import free_slots


class BookingForm(forms.Form):
    """The patient's booking form. The slot list contains only this doctor's free slots."""
    slot = forms.ModelChoiceField(
        queryset=None, widget=forms.RadioSelect, empty_label=None,
        error_messages={"invalid_choice": "This slot is no longer free. Please choose another one."})
    name = forms.CharField(max_length=100, label="Your name")
    phone = forms.CharField(max_length=15, label="Mobile number", help_text="10 digits, for example 98250 12345")
    reason = forms.CharField(max_length=200, required=False, label="Reason for the visit",
                             widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, doctor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slot"].queryset = free_slots(doctor)
        self.fields["slot"].label_from_instance = lambda s: f"{s.date:%a %d %b} at {s.start_time:%H:%M}"

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())          # "  asha   verma " -> "asha verma"

    def clean_phone(self):
        digits = "".join(ch for ch in self.cleaned_data["phone"] if ch.isdigit())
        if len(digits) != 10:
            raise forms.ValidationError("Enter a 10-digit mobile number.")
        return f"{digits[:5]} {digits[5:]}"                          # stored as "98250 12345"


class PatientForm(forms.ModelForm):
    """A form built from the Patient model (used by the reception page in the Do It Yourself section)."""

    class Meta:
        model = Patient
        fields = ["name", "phone", "date_of_birth"]
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def clean_date_of_birth(self):
        dob = self.cleaned_data["date_of_birth"]
        if dob and dob > date.today():
            raise forms.ValidationError("The date of birth cannot be in the future.")
        return dob


class SlotForm(forms.ModelForm):
    """Session 09: create and edit time slots on the management pages."""
    OPEN, CLOSE = time(8, 0), time(20, 0)

    class Meta:
        model = TimeSlot
        fields = ["doctor", "date", "start_time"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}),
                   "start_time": forms.TimeInput(attrs={"type": "time", "step": 1800})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)

    def clean_start_time(self):
        start = self.cleaned_data["start_time"]
        if not self.OPEN <= start <= self.CLOSE:      # the CheckConstraint stays as the safety net
            raise forms.ValidationError("The clinic is open from 08:00 to 20:00.")
        return start


class ReportForm(forms.ModelForm):
    """Session 12: upload one report. The model field's validators check type, size and content."""

    class Meta:
        model = Report
        fields = ["file"]
        labels = {"file": "Report (PDF, JPG or PNG, at most 2 MB)"}
