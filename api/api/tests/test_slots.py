"""Session 22: written after reading the coverage report: SlotViewSet.destroy() had no test."""
from clinic.models import TimeSlot


def test_free_slot_can_be_deleted(login, reception, clinic):
    slot = clinic["slots"][3]
    assert login(reception).delete(f"/api/v1/slots/{slot.pk}/").status_code == 204
    assert not TimeSlot.objects.filter(pk=slot.pk).exists()


def test_slot_with_an_appointment_cannot_be_deleted(login, reception, booked):
    response = login(reception).delete(f"/api/v1/slots/{booked.slot.pk}/")
    assert response.status_code == 409
    assert response.json()["error"]["message"] == "This slot has appointments and cannot be deleted."
