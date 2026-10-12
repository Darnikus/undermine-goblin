import random
import time
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from economy.models import Item, PriceHistory
from economy.scraper import Region, Scraper, managed_browser


class Command(BaseCommand):
    help = "Scrapes hourly item data from Undermine.Exchange."

    def handle(self, *args: Any, **options: Any) -> str | None:
        # Add random jitter 0 to 5 minutes
        delay = random.randint(0, 300)
        self.stdout.write(f"Waiting {delay} seconds before scraping...")
        time.sleep(delay)

        self.stdout.write("Starting hourly item scrape...")

        region = Region[getattr(settings, "REGION", "EU")]
        items = list(Item.objects.all())
        if not items:
            self.stdout.write(self.style.WARNING("No items found in the db."))
            return

        scraped_results = []
        with managed_browser(headless=False) as page:
            scraper: Scraper = Scraper(page, region=region)

            for item in items:
                try:
                    self.stdout.write(f"Scraping: {item.name} (ID: {item.id})")

                    data = scraper.scrape_item(item.id)

                    scraped_results.append(
                        {
                            "region": data["region"],
                            "item": item,
                            "name": data["name"],
                            "server": data["server"],
                            "price": data["price"],
                        }
                    )

                    self.stdout.write(self.style.SUCCESS(f"-> Success: {data}"))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"-> Failed to scrape {item.name}: {e}")
                    )

                time.sleep(random.uniform(1.5, 3.0))

        self.stdout.write(self.style.SUCCESS("Scrape comlete!"))

        for entry in scraped_results:
            item: Item = entry["item"]

            updated_fields = []
            if item.name == "":
                item.name = entry["name"]
                updated_fields.append("name")

            if updated_fields:
                item.save(update_fields=updated_fields)

            PriceHistory.objects.create(
                item=item, server=entry["server"], price=entry["price"]
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved {entry} to database!")
            )
