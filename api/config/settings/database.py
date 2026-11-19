"""Module 9, Session 16: the database settings from one address, DATABASE_URL.
Hosts such as Neon and Render give the database as one address:
    postgresql://USER:PASSWORD@HOST:PORT/NAME?sslmode=require
database_from_url() turns it into Django's DATABASES entry. Everything after
the ? goes to PostgreSQL as connection options (sslmode, channel_binding, ...).
A / : # ? or @ in the password must be written %2F %3A %23 %3F %40.
The error messages never repeat the address: it holds the password."""
from urllib.parse import parse_qsl, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

HINT = " (in the password, write / : # ? @ as %2F %3A %23 %3F %40)"


def database_from_url(url, connect_timeout=5):
    parts = urlsplit(url)
    if parts.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured("DATABASE_URL must start with postgresql://")
    name = unquote(parts.path.lstrip("/"))
    if not (parts.hostname and parts.username and name):
        raise ImproperlyConfigured(
            "DATABASE_URL needs a user, a host and a database name" + HINT)
    try:
        port = parts.port or 5432
    except ValueError:      # Python's own message would show part of the password
        raise ImproperlyConfigured(
            "DATABASE_URL has a port that is not a number" + HINT) from None
    options = {"connect_timeout": connect_timeout}
    options.update(parse_qsl(parts.query))
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": unquote(parts.username),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname,
        "PORT": str(port),
        "OPTIONS": options,
    }


def describe(db):
    """The settings without the password: safe to print or log."""
    options = " ".join(f"{k}={v}" for k, v in sorted(db["OPTIONS"].items()))
    return (f"user={db['USER']} host={db['HOST']} port={db['PORT']} "
            f"name={db['NAME']} password={len(db['PASSWORD'])} characters "
            f"options: {options}")
