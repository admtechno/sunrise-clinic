from django.apps import AppConfig


class ClinicConfig(AppConfig):
    name = "clinic"

    def ready(self):                                     # Session 23: runs once, when Django starts
        from . import signals  # noqa: F401              # importing the module connects its @receiver functions
