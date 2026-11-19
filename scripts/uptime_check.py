"""Module 9, Session 20: a small uptime check, the way a monitoring service
works: ask /ready/ again and again, and report only when the state changes.
    python scripts/uptime_check.py https://sunrise-api.onrender.com
           [--every 60] [--times 0] [--timeout 10]
--times 0 runs until Ctrl+C. It only reads: GET, no login."""
import argparse
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("base")
parser.add_argument("--every", type=float, default=60)      # seconds
parser.add_argument("--times", type=int, default=0)         # 0: for ever
parser.add_argument("--timeout", type=float, default=10)
args = parser.parse_args()
url = args.base.rstrip("/") + "/ready/"


def probe():
    """UP or DOWN, and why."""
    try:
        with urllib.request.urlopen(url, timeout=args.timeout) as response:
            return "UP", f"{response.status}"
    except urllib.error.HTTPError as error:          # the API answered: 503
        return "DOWN", f"{error.code}"
    except OSError as error:                         # no answer at all
        return "DOWN", f"no answer ({type(error).__name__})"


state, since, n = None, 0, 0
try:
    while args.times == 0 or n < args.times:
        n += 1
        new, why = probe()
        if new != state:
            note = f", after {n - since} checks {state}" if state else ""
            print(f"{new} ({why}){note}", flush=True)
            state, since = new, n
        time.sleep(args.every)
except KeyboardInterrupt:
    pass
print(f"{n} checks, now {state}")
