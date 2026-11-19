"""Session 16: every API error leaves in the same JSON shape:
{"error": {"status": 400, "code": "invalid", "message": "...", "fields": {...}}}"""
from rest_framework import exceptions
from rest_framework.views import exception_handler


def json_errors(exc, context):
    response = exception_handler(exc, context)               # DRF's own handler builds the response first
    if response is None:                                     # not an API error (a real bug): Django shows 500
        return None
    error = {"status": response.status_code}
    if isinstance(exc, exceptions.ValidationError):
        error["code"] = "invalid"
        error["message"] = "Some fields are not valid."
        data = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        error["fields"] = data
    else:
        detail = response.data.get("detail", response.data) if isinstance(response.data, dict) else response.data
        error["code"] = getattr(detail, "code", None) or getattr(exc, "default_code", "error")
        error["message"] = str(detail)
    response.data = {"error": error}
    return response


class Conflict(exceptions.APIException):
    """409: the request clashes with what is stored, e.g. deleting a slot that has appointments."""
    status_code = 409
    default_detail = "The request conflicts with the current data."
    default_code = "conflict"
