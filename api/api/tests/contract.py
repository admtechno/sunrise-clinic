"""Module 9, Session 09: a contract check. The OpenAPI schema (drf-spectacular) is the
promise the API makes to the Clinic Desk; check_contract(response) checks that a real
answer keeps it. Two rules are stricter than OpenAPI's own: an answer may not carry a
field the schema does not list, and every error must have the error shape."""
import functools
import re

import jsonschema
from drf_spectacular.generators import SchemaGenerator

ERROR = {                                         # the shape of api/exceptions.py
    "type": "object", "required": ["error"], "additionalProperties": False,
    "properties": {"error": {
        "type": "object", "required": ["status", "code", "message"],
        "additionalProperties": False,
        "properties": {
            "status": {"type": "integer"}, "code": {"type": "string"},
            "message": {"type": "string"},
            "fields": {"type": "object"}}}}}


@functools.cache
def openapi():                                    # made once per test run
    return SchemaGenerator(api_version="v1").get_schema(request=None, public=True)


def strict(node):
    """OpenAPI 3.0 to JSON Schema: `nullable` becomes a type; no extra fields."""
    if isinstance(node, list):
        return [strict(n) for n in node]
    if not isinstance(node, dict):
        return node
    node = {key: strict(value) for key, value in node.items()}
    if node.pop("nullable", False):
        node = ({**node, "type": [node["type"], "null"]} if "type" in node
                else {"anyOf": [node, {"type": "null"}]})
    if node.get("type") == "object" and "properties" in node:
        node.setdefault("additionalProperties", False)
    return node


def operation(method, path):
    """The schema's entry for a real path: /api/v1/doctors/3/ is /doctors/{id}/."""
    for template, methods in openapi()["paths"].items():
        if re.fullmatch(re.sub(r"\{[^}]+\}", "[^/]+", template), path):
            if method.lower() in methods:
                return template, methods[method.lower()]
    raise AssertionError(f"{method} {path} is not in the OpenAPI schema")


def check_contract(response):
    method, path = response.request["REQUEST_METHOD"], response.request["PATH_INFO"]
    template, op = operation(method, path)
    code = str(response.status_code)
    if response.status_code >= 400:
        schema = ERROR                            # errors are not in the schema
    elif code not in op["responses"]:
        raise AssertionError(f"{method} {template}: {code} is not in the schema")
    else:
        content = op["responses"][code].get("content")
        if not content:                           # 204: no body is promised
            assert not response.content, f"{method} {template}: a body for {code}"
            return
        schema = content["application/json"]["schema"]
    document = {**strict(schema), "components": strict(openapi()["components"])}
    try:
        jsonschema.validate(response.json(), document)
    except jsonschema.ValidationError as e:
        where = "/".join(str(p) for p in e.absolute_path) or "(the whole body)"
        raise AssertionError(
            f"{method} {template} {code}: at {where}: {e.message}") from None
