from django.urls import path
from django.views.generic import RedirectView

from . import views, views_manage, views_reports

app_name = "clinic"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("doctors/", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/<int:doctor_id>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path("specialities/", views.SpecialityListView.as_view(), name="speciality_list"),
    path("specialities/<slug:slug>/", views.speciality_doctors, name="speciality_doctors"),
    path("doctors/<int:doctor_id>/book/", views.book, name="book"),
    path("book/done/", views.booking_done, name="booking_done"),
    path("my/appointments/", views.my_appointments, name="my_appointments"),
    path("my/appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="cancel_appointment"),
    path("doctor/schedule/", views.DoctorScheduleView.as_view(), name="doctor_schedule"),   # Session 11
    path("my/appointments/<int:appointment_id>/reports/", views_reports.reports, name="reports"),   # Session 12
    path("reports/<int:report_id>/download/", views_reports.download_report, name="download_report"),
    path("our-doctors/", RedirectView.as_view(pattern_name="clinic:doctor_list", permanent=True), name="old_doctors_page"),
    # Session 09: slot management (Session 11: staff with the timeslot permissions only)
    path("manage/slots/", views_manage.SlotListView.as_view(), name="slot_list"),
    path("manage/slots/new/", views_manage.SlotCreateView.as_view(), name="slot_create"),
    path("manage/slots/<int:pk>/edit/", views_manage.SlotUpdateView.as_view(), name="slot_update"),
    path("manage/slots/<int:pk>/delete/", views_manage.SlotDeleteView.as_view(), name="slot_delete"),
]
