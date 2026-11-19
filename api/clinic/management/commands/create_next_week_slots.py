"""Session 23: python manage.py create_next_week_slots [--start 2026-12-07] [--doctor 1] [--dry-run]
Makes Monday-to-Friday slots for next week for every active doctor. Safe to run twice."""
from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinic.models import Doctor, TimeSlot

TIMES = [time(10, 0), time(10, 30), time(11, 0), time(11, 30)]


def next_monday(today):
    return today + timedelta(days=7 - today.weekday())   # weekday(): Monday is 0


class Command(BaseCommand):
    help = "Create next week's slots (Monday to Friday, 10:00 to 11:30) for active doctors."

    def add_arguments(self, parser):
        parser.add_argument("--start", help="the Monday to start from, YYYY-MM-DD (default: next Monday)")
        parser.add_argument("--doctor", type=int, help="only this doctor id")
        parser.add_argument("--dry-run", action="store_true", help="show what would be created, change nothing")

    def handle(self, *args, start=None, doctor=None, dry_run=False, **options):
        monday = datetime.strptime(start, "%Y-%m-%d").date() if start else next_monday(date.today())
        if monday.weekday() != 0:
            raise CommandError(f"{monday} is not a Monday.")
        doctors = Doctor.objects.filter(is_active=True).order_by("name")
        if doctor:
            doctors = doctors.filter(pk=doctor)
            if not doctors:
                raise CommandError(f"No active doctor with id {doctor}.")
        days = [monday + timedelta(days=n) for n in range(5)]
        total = 0
        with transaction.atomic():                       # all or nothing
            for d in doctors:
                created = 0
                for day in days:
                    for t in TIMES:
                        if dry_run:
                            created += not TimeSlot.objects.filter(doctor=d, date=day, start_time=t).exists()
                        else:
                            _, new = TimeSlot.objects.get_or_create(doctor=d, date=day, start_time=t)
                            created += new
                total += created
                self.stdout.write(f"{d.name}: {created} new, {len(days) * len(TIMES) - created} already there")
        verb = "would be created" if dry_run else "created"
        self.stdout.write(self.style.SUCCESS(f"{total} slots {verb} for {days[0]:%d %b} to {days[-1]:%d %b %Y}."))
