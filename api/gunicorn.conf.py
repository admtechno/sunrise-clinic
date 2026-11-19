"""Module 9, Session 14: how gunicorn runs the API on a Linux server or in a container.
gunicorn reads this file from the folder it starts in:  gunicorn config.wsgi
(On Windows gunicorn does not run; Module 8 used waitress there.)"""
import os

# the host says which port (Render sets PORT); 8000 on your own PC
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
# worker processes: each answers one request at a time. 2 suits a free plan
# with 512 MB of memory; more workers need more memory, not only more CPU.
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
timeout = 30          # a worker stuck longer than this is restarted
accesslog = "-"       # one line per request, to the terminal: the host keeps it
# Session 20: who, what, the status, the size and how long it took (%(M)s: ms)
access_log_format = '%(h)s "%(r)s" %(s)s %(B)s %(M)sms "%(a)s"'
errorlog = "-"
