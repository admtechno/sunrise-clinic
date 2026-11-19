"""Health and readiness (Module 9, Session 14).
/health/ says the process runs and answers: it touches nothing else, so a slow
database never makes it fail. /ready/ says the API can do its work now: it asks
the database. Docker, Render and an uptime monitor call them without a login.
Session 17: /health/ also names the version that runs (Render's commit)."""
import logging
import os

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

log = logging.getLogger("clinic")


@require_safe  # GET and HEAD only
@never_cache  # a cached "ok" would hide a server that stopped
def health(request):
    # Render sets RENDER_GIT_COMMIT to the commit it deployed; 7 characters
    # are enough to tell versions apart, as in `git log --oneline`
    version = os.environ.get("RENDER_GIT_COMMIT", "")[:7] or "local"
    return JsonResponse({"status": "up", "version": version})


@require_safe
@never_cache
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:  # any reason: the API cannot answer with data now
        log.exception("ready: the database does not answer")
        # the details go to the log, never to an address anyone can call
        return JsonResponse({"status": "not ready", "database": "unavailable"},
                            status=503)
    return JsonResponse({"status": "ready", "database": "ok"})
