"""Session 23: the number of SQL queries is part of the API's behaviour, so tests check it."""
from datetime import time

from django.db import connection
from django.test.utils import CaptureQueriesContext

from clinic.models import Appointment, TimeSlot


def queries_for(api, url):
    with CaptureQueriesContext(connection) as queries:
        assert api.get(url).status_code == 200
    return len(queries)


def test_appointment_list_does_not_grow_with_rows(login, reception, booked, clinic):
    api = login(reception)
    queries_for(api, "/api/v1/appointments/")             # warm-up: Django keeps the user's permissions after this
    one = queries_for(api, "/api/v1/appointments/?page_size=20")
    meera = clinic["meera"]
    for hour in range(13, 18):                            # five more appointments
        slot = TimeSlot.objects.create(doctor=meera, date=booked.slot.date, start_time=time(hour, 0))
        Appointment.objects.create(slot=slot, patient=booked.patient)
    six = queries_for(api, "/api/v1/appointments/?page_size=20")
    assert six == one                                     # select_related: no query per row


def test_appointment_list_query_count(login, reception, booked, django_assert_num_queries):
    api = login(reception)
    with django_assert_num_queries(4) as captured:        # 2 for the permissions, COUNT(*), the page
        api.get("/api/v1/appointments/")
    assert [q["sql"].split()[1] for q in captured.captured_queries][-2:] == ["COUNT(*)", '"clinic_appointment"."id",']


def test_stats_come_from_the_cache(api, clinic, django_assert_num_queries):
    first = api.get("/api/v1/stats/")
    assert first["X-Cache"] == "MISS"
    assert first.json() == {"active_doctors": 3, "free_slots": 4, "booked_appointments": 0}
    with django_assert_num_queries(0):                    # the second answer needs no database at all
        second = api.get("/api/v1/stats/")
    assert second["X-Cache"] == "HIT" and second.json() == first.json()


def test_a_booking_clears_the_stats(login, asha, clinic):
    api = login(asha.user)
    api.get("/api/v1/stats/")                             # now cached
    api.post("/api/v1/appointments/", {"slot": clinic["slots"][0].pk}, format="json")
    response = api.get("/api/v1/stats/")
    assert response["X-Cache"] == "MISS"                  # the signal deleted the cached numbers
    assert response.json()["booked_appointments"] == 1


def test_specialities_list_is_cached(api, clinic, django_assert_num_queries):
    api.get("/api/v1/specialities/")
    with django_assert_num_queries(0):
        assert api.get("/api/v1/specialities/").json()["count"] == 2
