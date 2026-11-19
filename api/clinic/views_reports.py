"""Session 12: patients upload reports for their own appointments; only the patient and the
appointment's doctor may download them. The files are never served from a public URL."""
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReportForm
from .models import Appointment, Report

logger = logging.getLogger(__name__)


@login_required
def reports(request, appointment_id):
    appointment = get_object_or_404(Appointment.objects.select_related("slot__doctor"),
                                    pk=appointment_id, patient__user=request.user)   # own appointments only
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)           # files arrive in request.FILES
        if form.is_valid():
            report = form.save(commit=False)
            report.appointment = appointment
            report.original_name = request.FILES["file"].name[:200]
            report.size = request.FILES["file"].size
            report.save()
            logger.info("Report %s uploaded for appointment %s (%s bytes)", report.pk, appointment.pk, report.size)
            messages.success(request, f"{report.original_name} uploaded.")
            return redirect("clinic:reports", appointment_id=appointment.pk)
        logger.warning("Upload refused for appointment %s: %s", appointment.pk, "; ".join(form.errors["file"]))
    else:
        form = ReportForm()
    return render(request, "clinic/reports.html",
                  {"appointment": appointment, "form": form, "reports": appointment.reports.all()})


@login_required
def download_report(request, report_id):
    allowed = Report.objects.filter(Q(appointment__patient__user=request.user) |       # the patient
                                    Q(appointment__slot__doctor__user=request.user))   # or their doctor
    report = get_object_or_404(allowed, pk=report_id)
    return FileResponse(report.file.open("rb"), as_attachment=True, filename=report.original_name)
