"""Module 9, Session 17: a few quick checks of a deployed API, after each deploy.
    python scripts/smoke_test.py https://sunrise-api.onrender.com
           [--origin https://sunrise-desk.example] [--expect-version 3f9c2a1]
--origin: the web app's address, for the CORS check. --expect-version: the
commit you pushed (git rev-parse --short HEAD); fails while the old one runs.
It only reads: GET and OPTIONS, no login. Exit code 1 if a check fails."""
import argparse
import json
import sys
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("base")
parser.add_argument("--origin", default="")
parser.add_argument("--expect-version", default="")      # DIY
args = parser.parse_args()
base = args.base.rstrip("/")
failed = 0


def ask(path, method="GET", headers=None):
    request = urllib.request.Request(base + path, method=method,
                                     headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:             # 4xx and 5xx answers
        return error.code, error.headers, error.read()


def check(name, ok, detail=""):
    global failed
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""))
    failed += not ok


status, _, _ = ask("/ready/")
check("/ready/ answers 200", status == 200, str(status))
if status != 200:
    sys.exit(1)
status, _, body = ask("/health/")
version = json.loads(body)["version"]
check("/health/ answers 200", status == 200, "version " + version)
if args.expect_version:                                   # DIY
    check("the new version is live", version == args.expect_version[:7],
          f"expected {args.expect_version[:7]}")
status, headers, body = ask("/api/v1/doctors/")
# json.loads only on a 200: a 500 page is HTML, and parsing it would crash
# the smoke test instead of letting it report FAIL
count = json.loads(body)["count"] if status == 200 else None
check("the doctors list", status == 200,
      f"{count} doctors" if count is not None else f"status {status}")
check("HSTS", "max-age" in headers.get("Strict-Transport-Security", ""))
check("no MIME sniffing", headers.get("X-Content-Type-Options") == "nosniff")
check("not in a frame", headers.get("X-Frame-Options") == "DENY")
status, _, body = ask("/no-such-page/")
check("DEBUG is off", status == 404 and b"DEBUG = True" not in body, str(status))
if args.origin:
    preflight = {"Origin": args.origin,
                 "Access-Control-Request-Method": "GET"}
    _, headers, _ = ask("/api/v1/doctors/", "OPTIONS", preflight)
    allowed = headers.get("Access-Control-Allow-Origin")
    check("CORS for the web app", allowed == args.origin)
    _, headers, _ = ask("/api/v1/doctors/", "OPTIONS",
                        {**preflight, "Origin": "https://other.example"})
    check("CORS refuses another site",
          "Access-Control-Allow-Origin" not in headers)
print("smoke test passed" if not failed else f"{failed} check(s) failed")
sys.exit(1 if failed else 0)
