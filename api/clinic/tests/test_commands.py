"""Session 23: the create_next_week_slots management command, run with call_command()."""
from datetime import date
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from clinic.models import TimeSlot


def run(*args):
    out = StringIO()
    call_command("create_next_week_slots", *args, stdout=out)
    return out.getvalue()


def test_creates_twenty_slots_per_doctor(doctor):
    output = run("--start", "2026-12-07")
    assert TimeSlot.objects.filter(doctor=doctor).count() == 20      # 5 days x 4 times
    assert "20 slots created for 07 Dec to 11 Dec 2026." in output


def test_running_twice_creates_nothing_new(doctor):
    run("--start", "2026-12-07")
    assert "0 slots created" in run("--start", "2026-12-07")
    assert TimeSlot.objects.count() == 20


def test_dry_run_changes_nothing(doctor):
    assert "20 slots would be created" in run("--start", "2026-12-07", "--dry-run")
    assert TimeSlot.objects.count() == 0


def test_start_must_be_a_monday(doctor):
    with pytest.raises(CommandError, match="is not a Monday"):
        run("--start", "2026-12-08")


def test_next_monday():
    from clinic.management.commands.create_next_week_slots import next_monday
    assert next_monday(date(2026, 11, 11)) == date(2026, 11, 16)     # a Wednesday -> the next Monday
    assert next_monday(date(2026, 11, 16)) == date(2026, 11, 23)     # a Monday -> one week later
