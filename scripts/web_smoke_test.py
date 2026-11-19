"""Module 9, Session 18 (mini challenge): quick checks of the deployed web app.
    python scripts/web_smoke_test.py https://sunrise-desk.vercel.app
It only reads: GET, no login. Exit code 1 if a check fails."""
import re
import sys
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")
failed = 0


def ask(path):
    try:
        with urllib.request.urlopen(base + path, timeout=15) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:              # 4xx and 5xx answers
        return error.code, error.headers, error.read()


def check(name, ok, detail=""):
    global failed
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""))
    failed += not ok


status, headers, page = ask("/")
check("the page", status == 200 and b'<div id="root">' in page, str(status))
check("no MIME sniffing", headers.get("X-Content-Type-Options") == "nosniff")
status, headers, deep = ask("/schedule")
check("a router address after a reload", status == 200 and deep == page)
script = re.search(rb'src="(/assets/[^"]+\.js)"', page).group(1).decode()
status, headers, _ = ask(script)
check("the page's script", status == 200
      and "javascript" in headers.get("Content-Type", ""), script.split("/")[-1])
check("cached for a year", "immutable" in headers.get("Cache-Control", ""))
status, headers, _ = ask("/assets/no-such-file.js")
check("a missing script is a 404, not the page", status == 404, str(status))
status, headers, body = ask("/api/v1/doctors/")
check("the API through the rewrite", status == 200
      and "json" in headers.get("Content-Type", ""), str(status))
print("web smoke test passed" if not failed else f"{failed} check(s) failed")
sys.exit(1 if failed else 0)
