"""Run from the project folder: python schema_summary.py schema.yml
Session 20: every path and method in an OpenAPI file, with its tag and operationId."""
import sys

import yaml

schema = yaml.safe_load(open(sys.argv[1]))
print(schema["openapi"], "|", schema["info"]["title"], schema["info"]["version"], "|", len(schema["paths"]), "paths")
for path, operations in schema["paths"].items():
    for method, op in operations.items():
        print(f"{method.upper():6} {path:42} {op['tags'][0]:13} {op['operationId']}")
print("security schemes:", ", ".join(schema["components"]["securitySchemes"]))
