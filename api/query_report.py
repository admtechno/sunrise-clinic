"""Run from the project folder: python query_report.py
Session 23: counts the SQL queries of the same work done in different ways. It adds 20 demo
appointments inside a transaction and rolls them back at the end, so your database is unchanged."""
import os
from datetime import date, time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
from django.db import connection, transaction  # noqa: E402
from django.db.models import Prefetch  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402

from clinic.models import Appointment, Doctor, Patient, TimeSlot  # noqa: E402


def count(label, work):
    """Run work() and print how many SQL queries it sent."""
    with CaptureQueriesContext(connection) as queries:
        result = work()
    print(f"{label:<50} {len(queries):>3} queries")
    return result, queries


def rows(appointments):                                  # what a list page or a serializer reads
    return [(a.patient.name, a.slot.doctor.name, a.slot.date) for a in appointments]


with transaction.atomic():
    asha = Patient.objects.get(pk=1)
    meera = Doctor.objects.get(name="Dr. Meera Shah")
    for hour in range(8, 18):                            # 20 demo slots and appointments
        for minute in (0, 30):
            slot = TimeSlot.objects.create(doctor=meera, date=date(2026, 12, 9), start_time=time(hour, minute))
            Appointment.objects.create(slot=slot, patient=asha)
    n = Appointment.objects.count()
    print(f"Appointments: {n}\n")

    print("1. Appointments with patient and doctor")
    count("   for a in Appointment.objects.all()", lambda: rows(Appointment.objects.all()))
    _, q = count('   ... .select_related("patient", "slot__doctor")',
                 lambda: rows(Appointment.objects.select_related("patient", "slot__doctor")))
    sql = q.captured_queries[0]["sql"]
    print("   the one query: SELECT ...", sql[sql.index(" FROM "):].replace(' INNER JOIN', '\n     INNER JOIN')[:400])

    print("\n2. Doctors with their slots")
    doctors = lambda: Doctor.objects.order_by("name")  # noqa: E731
    count("   for d in doctors: d.slots.all()", lambda: [list(d.slots.all()) for d in doctors()])
    count('   ... .prefetch_related("slots")', lambda: [list(d.slots.all()) for d in doctors().prefetch_related("slots")])
    free = TimeSlot.objects.exclude(appointments__status="booked").order_by("date", "start_time")
    result, q = count('   ... Prefetch("slots", free, to_attr="free")',
                      lambda: [(d.name, len(d.free)) for d in doctors().prefetch_related(
                          Prefetch("slots", queryset=free, to_attr="free"))])
    for sql in (x["sql"] for x in q.captured_queries):
        print("   SQL: SELECT ...", sql[sql.index(" FROM "):][:120], "...")
    print("   free slots per doctor:", ", ".join(f"{name.removeprefix('Dr. ')} {k}" for name, k in result))
    transaction.set_rollback(True)                       # throw the demo rows away
print("\nRolled back: the 20 demo appointments are gone.", Appointment.objects.count(), "appointments left.")
