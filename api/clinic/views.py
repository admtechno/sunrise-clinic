from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.db.models import Count, Exists, Min, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from .forms import BookingForm
from .models import Appointment, Doctor, Patient, Speciality, TimeSlot
from .services import SlotTaken, book_slot, cancel

SORTS = {"name": "name", "fee": "fee", "-fee": "-fee"}   # allowed ?sort= values
BOOKED = Appointment.objects.filter(status=Appointment.Status.BOOKED)


class HomeView(TemplateView):
    template_name = "clinic/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor_count"] = Doctor.objects.filter(is_active=True).count()
        context["specialities"] = Speciality.objects.all()
        return context


class DoctorListView(ListView):
    """Session 09: the Session 05 search as a class. ListView adds pagination."""
    template_name = "clinic/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 5

    def get_queryset(self):
        g = self.request.GET
        self.q, self.slug = g.get("q", "").strip(), g.get("speciality", "")
        self.max_fee, self.sort = g.get("max_fee", ""), g.get("sort", "name")
        doctors = Doctor.objects.filter(is_active=True).select_related("speciality")
        if self.q:
            doctors = doctors.filter(Q(name__icontains=self.q) | Q(speciality__name__icontains=self.q))
        if self.slug:
            doctors = doctors.filter(speciality__slug=self.slug)
        if self.max_fee.isdigit():
            doctors = doctors.filter(fee__lte=int(self.max_fee))
        if self.sort not in SORTS:
            self.sort = "name"
        return doctors.order_by(SORTS[self.sort], "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop("page", None)
        context.update(q=self.q, slug=self.slug, max_fee=self.max_fee, sort=self.sort,
                       specialities=Speciality.objects.all(), query=query.urlencode())
        return context


class SpecialityListView(ListView):
    template_name = "clinic/speciality_list.html"
    context_object_name = "specialities"
    queryset = Speciality.objects.annotate(
        active=Count("doctors", filter=Q(doctors__is_active=True)),
        lowest_fee=Min("doctors__fee", filter=Q(doctors__is_active=True)),
    ).order_by("name")   # Meta.ordering is not used in GROUP BY queries, so order explicitly


class DoctorDetailView(DetailView):
    queryset = Doctor.objects.select_related("speciality")
    pk_url_kwarg = "doctor_id"                 # the URL says <int:doctor_id>, not <int:pk>
    template_name = "clinic/doctor_detail.html"
    context_object_name = "doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slots"] = self.object.slots.annotate(booked=Exists(BOOKED.filter(slot=OuterRef("pk"))))
        recent = self.request.session.get("recent_doctors", [])      # ids only: sessions store JSON
        if self.object.pk in recent:
            recent.remove(self.object.pk)
        self.request.session["recent_doctors"] = [self.object.pk] + recent[:2]
        return context


def speciality_doctors(request, slug):
    speciality = get_object_or_404(Speciality, slug=slug)
    return redirect(f"{reverse('clinic:doctor_list')}?speciality={speciality.slug}")


def book(request, doctor_id):
    """GET shows the empty form; POST validates it, books the slot and redirects (Post/Redirect/Get)."""
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_active=True)
    if request.method == "POST":
        form = BookingForm(request.POST, doctor=doctor)
        if form.is_valid():
            data = form.cleaned_data
            patient, _ = Patient.objects.get_or_create(phone=data["phone"], defaults={"name": data["name"]})
            try:
                appointment = book_slot(data["slot"], patient, data["reason"])
            except SlotTaken:
                form.add_error("slot", "Sorry, someone booked this slot a moment ago. Please choose another one.")
            else:
                request.session["last_booking"] = appointment.id      # only this browser can see the confirmation
                messages.success(request, "Your appointment is booked.")
                return redirect("clinic:booking_done")
    else:
        patient = getattr(request.user, "patient", None) if request.user.is_authenticated else None
        initial = {"name": patient.name, "phone": patient.phone} if patient else {}
        form = BookingForm(doctor=doctor, initial=initial)
    return render(request, "clinic/book.html", {"doctor": doctor, "form": form})


def booking_done(request):
    appointment_id = request.session.get("last_booking")
    if appointment_id is None:
        return redirect("clinic:doctor_list")
    appointment = get_object_or_404(Appointment.objects.select_related("slot__doctor", "patient"), pk=appointment_id)
    return render(request, "clinic/booking_done.html", {"appointment": appointment})


@login_required
def my_appointments(request):
    patient = getattr(request.user, "patient", None)
    appointments = (patient.appointments.select_related("slot__doctor").order_by("slot__date", "slot__start_time")
                    if patient else Appointment.objects.none())
    ids = request.session.get("recent_doctors", [])
    recent = sorted(Doctor.objects.filter(pk__in=ids), key=lambda d: ids.index(d.pk))   # newest first
    return render(request, "clinic/my_appointments.html",
                  {"patient": patient, "appointments": appointments, "recent": recent})


@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    # patient__user=request.user: a patient can only find (and cancel) their own appointments
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient__user=request.user,
                                    status=Appointment.Status.BOOKED)
    cancel(appointment)
    messages.success(request, f"Your appointment on {appointment.slot.date:%d %b} is cancelled.")
    return redirect("clinic:my_appointments")


class DoctorScheduleView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Session 11: a doctor's own booked appointments. Only logins linked to a Doctor may open it."""
    template_name = "clinic/doctor_schedule.html"
    context_object_name = "appointments"

    def test_func(self):                     # False -> 403 Forbidden for logged-in users
        return getattr(self.request.user, "doctor", None) is not None

    def get_queryset(self):                  # filtered on request.user: never another doctor's list
        return (Appointment.objects.filter(slot__doctor=self.request.user.doctor, status=Appointment.Status.BOOKED)
                .select_related("slot", "patient"))
