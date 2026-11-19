"""Session 24: put a new random SECRET_KEY into .env without ever printing it.
Run it once on each server: python new_secret_key.py"""
from pathlib import Path

from django.core.management.utils import get_random_secret_key

env = Path(__file__).resolve().parent / ".env"
lines = [ln for ln in env.read_text().splitlines() if not ln.startswith("DJANGO_SECRET_KEY=")]
lines.insert(0, f"DJANGO_SECRET_KEY='{get_random_secret_key()}'")
env.write_text("\n".join(lines) + "\n")
print("A new SECRET_KEY is in .env (not shown). Everyone is logged out, and old JWT tokens stop working.")
