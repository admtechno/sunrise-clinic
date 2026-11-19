"""Session 19: who may do what in the API.
has_permission(): checked for every request to the view.
has_object_permission(): checked by get_object() for one appointment, after has_permission() passed."""
from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    message = "Only patients can book appointments."

    def has_permission(self, request, view):
        return hasattr(request.user, "patient")


class IsDoctor(permissions.BasePermission):
    message = "Only doctors can use this."

    def has_permission(self, request, view):
        return hasattr(request.user, "doctor")


class IsOwnerOrReception(permissions.BasePermission):
    """The patient of the appointment, or staff who may change appointments (Reception)."""
    message = "You can only cancel your own appointments."

    def has_object_permission(self, request, view, obj):
        return obj.patient.user_id == request.user.id or request.user.has_perm("clinic.change_appointment")


class IsSlotDoctor(permissions.BasePermission):
    """The doctor whose slot the appointment is in."""
    message = "You can only complete appointments in your own slots."

    def has_object_permission(self, request, view, obj):
        return obj.slot.doctor.user_id == request.user.id


class ReportRules(permissions.BasePermission):
    """Module 9, Session 07: the patient uploads; the patient and the doctor read."""
    def has_object_permission(self, request, view, obj):
        if obj.patient.user_id == request.user.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            self.message = "Only the patient and the doctor can see these reports."
            return obj.slot.doctor.user_id == request.user.id
        self.message = "Only the patient can upload reports."
        return False
