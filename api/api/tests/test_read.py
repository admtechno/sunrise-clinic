"""Session 22: reading the API as a visitor: status codes, JSON, pagination and filters."""
URL = "/api/v1"


def test_doctor_list_is_paginated(api, clinic):
    response = api.get(f"{URL}/doctors/")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    body = response.json()
    assert body["count"] == 3
    assert [d["name"] for d in body["results"]] == ["Dr. Arjun Patel", "Dr. Kavya Iyer", "Dr. Meera Shah"]
    assert body["next"] is None                  # three doctors fit on one page of three


def test_doctor_detail_shape(api, clinic):
    doctor = api.get(f"{URL}/doctors/{clinic['meera'].pk}/").json()
    assert doctor["speciality"] == {"id": clinic["meera"].speciality_id, "name": "General Medicine",
                                    "slug": "general-medicine"}
    assert doctor["fee"] == "500.00"             # DecimalField: a string, so no rounding errors


def test_free_slots_filter(api, clinic, booked):
    response = api.get(f"{URL}/slots/", {"doctor": clinic["meera"].pk, "free": "true"})
    assert [s["start_time"] for s in response.json()["results"]] == ["10:30"]   # 10:00 is booked


def test_unknown_doctor_is_404_in_our_error_shape(api, clinic):
    response = api.get(f"{URL}/doctors/9999/")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_v2_shows_the_fee_with_a_currency(api, clinic):
    v1 = api.get(f"{URL}/doctors/{clinic['meera'].pk}/").json()
    v2 = api.get(f"/api/v2/doctors/{clinic['meera'].pk}/").json()
    assert v1["fee"] == "500.00"
    assert v2["fee"] == {"amount": "500.00", "currency": "INR"}


def test_doctor_slots_action(api, clinic, booked):
    response = api.get(f"{URL}/doctors/{clinic['meera'].pk}/slots/")   # a custom @action (Session 15)
    assert response.status_code == 200
    assert [s["start_time"] for s in response.json()] == ["10:30"]
