"""Module 9, Session 20: what a piece of the API's log says, in a few lines.
    docker compose logs --no-log-prefix api | python scripts/log_summary.py
On Render: copy lines from the service's Logs page into a file, then
    python scripts/log_summary.py < lines.txt
It reads gunicorn's access lines (gunicorn.conf.py, Session 20) and the
ERROR and WARNING lines of Django and the clinic."""
import re
import sys
from collections import Counter

ACCESS = re.compile(r'^\S+ "(\w+) (\S+) [^"]*" (\d{3}) \S+ (\d+)ms')
by_status, by_path, problems = Counter(), Counter(), Counter()
for line in sys.stdin:
    m = ACCESS.match(line)
    if m:
        method, path, status = m.group(1), m.group(2).split("?")[0], m.group(3)
        by_status[status[0] + "xx"] += 1
        by_path[f"{method} {path} {status}"] += 1
    elif line.startswith(("ERROR", "WARNING")):
        problems[line.split(":")[0]] += 1
print(f"requests: {sum(by_status.values())}  " +
      "  ".join(f"{k}: {v}" for k, v in sorted(by_status.items())))
for key, count in by_path.most_common():
    if not key.endswith((" 200", " 201", " 204", " 304")):
        print(f"  {count} x {key}")
for key, count in sorted(problems.items()):
    print(f"  {count} x {key}")
