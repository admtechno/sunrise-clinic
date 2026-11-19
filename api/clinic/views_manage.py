"""Session 09: create, read, update and delete time slots with generic class-based views.
Session 11: each view needs a permission. Visitors are sent to the login page; logged-in users
without the permission get 403 Forbidden."""
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Exists, OuterRef, ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import SlotForm
from .models import Appointment, TimeSlot

BOOKED = Appointment.objects.filter(status=Appointment.Status.BOOKED, slot=OuterRef("pk"))


class SlotListView(PermissionRequiredMixin, ListView):   # template: clinic/timeslot_list.html
    permission_required = "clinic.view_timeslot"
    queryset = TimeSlot.objects.select_related("doctor").annotate(booked=Exists(BOOKED))
    paginate_by = 10


class SlotCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):   # template: clinic/timeslot_form.html
    permission_required = "clinic.add_timeslot"
    model = TimeSlot
    form_class = SlotForm
    success_url = reverse_lazy("clinic:slot_list")
    success_message = "Slot %(date)s %(start_time)s added."


class SlotUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):   # same template, form filled from the object
    permission_required = "clinic.change_timeslot"
    model = TimeSlot
    form_class = SlotForm
    success_url = reverse_lazy("clinic:slot_list")
    success_message = "Slot changed to %(date)s %(start_time)s."


class SlotDeleteView(PermissionRequiredMixin, DeleteView):   # template: clinic/timeslot_confirm_delete.html
    permission_required = "clinic.delete_timeslot"
    model = TimeSlot
    success_url = reverse_lazy("clinic:slot_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)     # deletes self.object
        except ProtectedError:                      # Appointment.slot uses on_delete=PROTECT
            messages.error(self.request, f"{self.object} has appointments and cannot be deleted.")
            return redirect("clinic:slot_list")
        messages.success(self.request, "Slot deleted.")
        return response
