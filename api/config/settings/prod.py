"""Settings for the real server (Session 24): every value that differs comes from the environment."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, LOGGING, MIDDLEWARE

DEBUG = False
# Module 9, Session 17: the names of DJANGO_ALLOWED_HOSTS, and on Render the
# service's own name (sunrise-api.onrender.com), which Render sets for you.
HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h for h in HOSTS.split(",") if h]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
if not ALLOWED_HOSTS:                                     # fails loudly when missing
    raise ImproperlyConfigured(
        "Set DJANGO_ALLOWED_HOSTS (Render: RENDER_EXTERNAL_HOSTNAME).")

# HTTPS (Session 24). On the real server all of these are on. On a PC without HTTPS,
# .env may set DJANGO_SSL_REDIRECT=0 and DJANGO_HSTS_SECONDS=0 for a local preview.
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SSL_REDIRECT", "1") == "1"   # http:// -> https://
# Module 9, Session 14: a host's health check calls these over plain HTTP, inside its network
SECURE_REDIRECT_EXEMPT = [r"^health/$", r"^ready/$"]
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))   # browsers: HTTPS only, 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")    # behind a proxy such as Nginx
SESSION_COOKIE_SECURE = True                                     # cookies only over HTTPS (Session 11)
CSRF_COOKIE_SECURE = True
JWT_COOKIE_SECURE = True                                         # Module 9, Session 05: the refresh cookie too
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

# HSTS preload (security.W021) puts the domain on a list built into browsers: HTTPS only, for
# months, even if you change your mind. Only the owner of the domain decides that, so we silence it.
SILENCED_SYSTEM_CHECKS = ["security.W021"]

# Email (Session 24): the console backend of base.py only prints; the server sends real email by SMTP.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {"host": os.environ.get("EMAIL_HOST", "localhost"), "port": int(os.environ.get("EMAIL_PORT", "587")),
                    "username": os.environ.get("EMAIL_HOST_USER", ""), "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
                    "use_tls": True},
    },
}

# Static files (Session 24): collectstatic copies every CSS and JS file into STATIC_ROOT;
# WhiteNoise serves them from there, with a hash in each file name so browsers may cache them for ever.
STATIC_ROOT = BASE_DIR / "staticfiles"
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
                  "whitenoise.middleware.WhiteNoiseMiddleware")   # right after SecurityMiddleware
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Module 9, Session 15: in a container the log goes to the terminal
# only (Docker and the host keep it); DJANGO_LOG_TO_FILE=0 switches the file off.
LOG_TO_FILE = os.environ.get("DJANGO_LOG_TO_FILE", "1") == "1"
LOG_HANDLERS = ["console", "file"] if LOG_TO_FILE else ["console"]
LOG_DIR = BASE_DIR / "logs"
if LOG_TO_FILE:
    LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    **LOGGING,
    "formatters": {**LOGGING["formatters"],
                   "timed": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
    "handlers": {**LOGGING["handlers"], **({} if not LOG_TO_FILE else {
                 "file": {"class": "logging.handlers.RotatingFileHandler", "filename": LOG_DIR / "clinic.log",
                          "maxBytes": 1_000_000, "backupCount": 5, "formatter": "timed"}})},
    "loggers": {"clinic": {"handlers": LOG_HANDLERS, "level": "INFO"},
                "django.request": {"handlers": LOG_HANDLERS, "level": "ERROR"},   # every 500, with its traceback
                "django.security": {"handlers": LOG_HANDLERS, "level": "ERROR"}},  # for example a wrong Host
}
