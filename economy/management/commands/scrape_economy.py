import random
import time
from typing import Any

from django.core.management.base import BaseCommand

from economy.models import Item, PriceHistory
from economy.scraper import Scraper, managed_browser


class Command(BaseCommand):
    help = "Scrapes hourly item data from Undermine.Exchange."

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Starting hourly item scrape...")

        items = list(Item.objects.all())
        if not items:
            self.stdout.write(self.style.WARNING("No items found in the db."))
            return

        scraped_results = []
        with managed_browser(headless=False) as page:
            scraper: Scraper = Scraper(page)  # TODO switching regions

            for item in items:
                try:
                    self.stdout.write(f"Scraping: {item.name} (ID: {item.id})")

                    data = scraper.scrape_item(item.id)

                    scraped_results.append(
                        {"item": item, "server": data["server"], "price": data["price"]}
                    )

                    self.stdout.write(self.style.SUCCESS(f"-> Success: {data}"))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"-> Failed to scrape {item.name}: {e}")
                    )

                time.sleep(random.uniform(1.5, 3.0))

        self.stdout.write(self.style.SUCCESS("Scrape comlete!"))

        for entry in scraped_results:
            PriceHistory.objects.create(
                item=entry["item"], server=entry["server"], price=entry["price"]
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved {entry} to database!")
            )
