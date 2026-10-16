from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Sets up the price scraper schedule and starts Django-Q cluster."

    def handle(self, *args: Any, **options: Any) -> str | None:
        _, created = Schedule.objects.get_or_create(
            func="economy.tasks.run_scraper",
            schedule_type=Schedule.HOURLY,
            name="Hourly Undermine.exchange Scraper",
            defaults={
                "repeats": -1,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully created `Hourly Undermine.exchange Scraper` schedule!"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Schedule alreasy exists and is up to date.")
            )

        self.stdout.write(
            self.style.SUCCESS("Starting Django-Q cluster... (Press Ctrl+C to stop)")
        )
        call_command("qcluster")
