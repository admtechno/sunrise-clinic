#!/bin/sh
# Module 9, Session 17: what Render runs when a new version of the API starts
# (render.yaml: dockerCommand: sh start.sh). The free plan has no pre-deploy
# step, so the migrations run here first, through the DIRECT address
# (Session 16), and gunicorn starts only if they succeeded.
set -e
if [ -n "$DATABASE_DIRECT_URL" ]; then
  echo "start.sh: migrating through the direct address"
  DATABASE_URL="$DATABASE_DIRECT_URL" python manage.py migrate --noinput
else
  echo "start.sh: DATABASE_DIRECT_URL is not set, no migrations"
fi
exec gunicorn config.wsgi        # exec: gunicorn gets Render's stop signal
