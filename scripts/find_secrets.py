"""Module 9, Session 16: look for secrets in the files Git tracks.
    python scripts/find_secrets.py     (in the project, before every push)
It prints the file, the line and the NAME of what it found, never the
value, so the report itself is safe to share. Exit code 1 if it finds any.
A line that holds the words not-a-secret is skipped: mark made-up examples."""
import re
import subprocess
import sys

KEYS = r"[A-Z0-9_]*(SECRET|PASSWORD|TOKEN|API_KEY)[A-Z0-9_]*"
NAMED = re.compile(rf"^\s*({KEYS})\s*[=:]\s*(.*)$")
URL = re.compile(r"postgres(ql)?://[^:/@\s]+:([^@\s]+)@")
# A real secret is one long word. <your value>, ${NAME}, os.environ[...]
# and PASSWORD are not.
SECRET = re.compile(r"^[A-Za-z0-9_\-+/=.%@!~]{8,}$")
PLACEHOLDER = re.compile(r"^[A-Z_]+$")


def looks_secret(value):
    value = value.split(" #")[0].strip().strip("'\"")
    return bool(SECRET.match(value)) and not PLACEHOLDER.match(value)


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                         text=True, check=True).stdout
    return [name for name in out.split("\0") if name]


files = tracked_files()
found = 0
for name in files:
    try:
        with open(name, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError):
        continue                           # pictures and other binary files
    for number, line in enumerate(lines, 1):
        if "not-a-secret" in line:
            continue
        named = NAMED.match(line)
        if named and looks_secret(named.group(3)):
            print(f"{name}:{number}: a value for {named.group(1)}")
            found += 1
        url = URL.search(line)
        if url and looks_secret(url.group(2)):
            print(f"{name}:{number}: a database address with a password in it")
            found += 1
print(f"{found} possible secret(s) in {len(files)} tracked files")
sys.exit(1 if found else 0)
