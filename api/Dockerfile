# Module 9, Session 15: the Sunrise Clinic API in a container.
#   docker build -t sunrise-api .        (in the api folder)
# The image holds the code and its packages, never a secret: the SECRET_KEY,
# the database password and the host names come from the environment when the
# container starts (docker compose, or Render in Session 17).
FROM python:3.13-slim

# no .pyc files, log lines at once, no pip cache in the image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# 1. the packages first: this layer is rebuilt only when requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. then the code (.dockerignore keeps .venv, .env and the rest out)
COPY . .

# 3. static files for WhiteNoise. The settings need these names to load; the
#    values are placeholders for this one command and are NOT the real secrets.
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    DJANGO_SECRET_KEY=collectstatic-only-not-a-secret \
    DJANGO_ALLOWED_HOSTS=build DB_NAME=build DB_USER=build \
    python manage.py collectstatic --noinput

# 4. never run as root: a user of its own, allowed to write only logs and media
#    (-R: collectstatic, run as root above, already made logs/clinic.log)
RUN useradd --create-home --uid 10001 clinic \
    && mkdir -p logs media \
    && chown -R clinic:clinic logs media
USER clinic

ENV DJANGO_SETTINGS_MODULE=config.settings.prod PORT=8000
EXPOSE 8000
# Docker asks /health/ every 10 seconds; `docker ps` shows healthy or unhealthy
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health/' % os.environ['PORT'], timeout=2)"
# gunicorn reads gunicorn.conf.py: 0.0.0.0:$PORT, WEB_CONCURRENCY workers
CMD ["gunicorn", "config.wsgi"]
