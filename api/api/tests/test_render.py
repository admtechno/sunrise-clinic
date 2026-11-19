"""Module 9, Session 17: the production settings on Render."""
import subprocess
import sys

CODE = ("import django, os; os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod';"
        " django.setup(); from django.conf import settings;"
        " print(settings.ALLOWED_HOSTS, settings.CSRF_TRUSTED_ORIGINS)")
# DJANGO_ALLOWED_HOSTS empty, not missing: then .env (load_dotenv) cannot fill it in
BASE = {"DJANGO_SECRET_KEY": "x" * 50, "DB_NAME": "x", "DB_USER": "x",  # not-a-secret
        "DJANGO_ALLOWED_HOSTS": "", "DJANGO_LOG_TO_FILE": "0", "PATH": "/usr/bin:/bin"}


def settings_with(**env):
    return subprocess.run([sys.executable, "-c", CODE], env={**BASE, **env},
                          capture_output=True, text=True)


def test_render_adds_its_own_host_name():
    result = settings_with(RENDER_EXTERNAL_HOSTNAME="sunrise-api.onrender.com")
    assert result.returncode == 0, result.stderr
    assert "['sunrise-api.onrender.com'] ['https://sunrise-api.onrender.com']" in result.stdout


def test_both_lists_are_joined():
    result = settings_with(DJANGO_ALLOWED_HOSTS="api.sunrise.example",
                           RENDER_EXTERNAL_HOSTNAME="sunrise-api.onrender.com")
    assert "['api.sunrise.example', 'sunrise-api.onrender.com']" in result.stdout


def test_no_host_name_at_all_is_refused():
    result = settings_with()
    assert result.returncode == 1
    assert "Set DJANGO_ALLOWED_HOSTS" in result.stderr


def test_a_database_url_alone_is_enough():
    # Render gives only DATABASE_URL: DB_NAME and DB_USER must not be needed
    env = {k: v for k, v in BASE.items() if k not in ("DB_NAME", "DB_USER")}
    result = subprocess.run(
        [sys.executable, "-c", CODE], capture_output=True, text=True,
        env={**env, "RENDER_EXTERNAL_HOSTNAME": "sunrise-api.onrender.com",
             "DATABASE_URL": "postgresql://u:p@h/db?sslmode=require"})  # not-a-secret
    assert result.returncode == 0, result.stderr
