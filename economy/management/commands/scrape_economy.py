import random
import time
from decimal import Decimal
from typing import Any

import requests
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

        DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
        DISCORD_CHANNEL_ID = settings.DISCORD_CHANNEL_ID
        if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
            self.stdout.write(
                self.style.WARNING(
                    "Missing Discord configuration (Bot token or Channel ID)."
                )
            )
            return
        url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"

        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
        }

        region = Region[getattr(settings, "REGION", "EU")]
        items = list(Item.objects.all())
        if not items:
            self.stdout.write(self.style.WARNING("No items found in the db."))
            return

        scraped_results: list[dict[str, Any]] = []
        with managed_browser(headless=True) as page:
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
                            "url": data["url"],
                            "icon_url": data["icon_url"],
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

            previous_price_history = item.prices.last()
            first_price_history = item.prices.first()

            current_price_history = PriceHistory.objects.create(
                item=item, server=entry["server"], price=entry["price"]
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully saved {entry} to database!")
            )

            payload = {
                "embeds": self._format_embed_payload(
                    current_price_history,
                    previous_price_history,
                    first_price_history,
                    entry["region"],
                    entry["url"],
                    entry["icon_url"],
                )
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        "-> Failed to send message:"
                        + f"{response.status_code}, {response.text}"
                    )
                )

    @staticmethod
    def _format_decimal_to_string(price: Decimal) -> str:
        """Converts the price from a decimal to a string format.

        Args:
            price (Decimal): An item's price.

        Returns:
            str: An item's price in str.
        """
        gold, silver = divmod(price, 1)
        silver = int(silver * 100)

        return f"{int(gold)}g {silver:02d}s"

    @staticmethod
    def _format_embed_payload(
        current_price_history: PriceHistory,
        previous_price_history: PriceHistory | None,
        first_price_history: PriceHistory | None,
        region: str,
        item_url: str,
        icon_url: str,
    ) -> list[dict[str, Any]]:
        """Formats a message as a Discord embed.

        Args:
            current_price_history (PriceHistory): Current PriceHistory instance.
            previous_price_history (PriceHistory | None): Previous PriceHistory
             instance.
            first_price_history (PriceHistory | None): First tracked PriceHistory
             instance.
            region (str): Selected region.
            item_url (str): Url of the tracked item.
            icon_url (str): Url of item's icon.

        Returns:
            list[dict[str, Any]]: An embed ready to be included in the payload.
        """
        NEUTRAL_COLOR = 9807270  # Gray
        GREEN_COLOR = 5763719  # Green color for price went down
        RED_COLOR = 15548997  # Red color for price went up

        item: Item = current_price_history.item

        if not first_price_history:
            first_price_text = "-"
        else:
            first_price_text = Command._format_price_change(
                current_price_history.price,
                first_price_history.price,
                is_first_price=True,
            )

        if not previous_price_history or previous_price_history == first_price_history:
            previous_price_text = "-"
        else:
            previous_price_text = Command._format_price_change(
                current_price_history.price, previous_price_history.price
            )

        if (
            not previous_price_history
            or current_price_history.price == previous_price_history.price
        ):
            title_prefix = "Price Update"
            embed_color = NEUTRAL_COLOR
            current_icon = "⚪"
        else:
            has_price_increased = (
                current_price_history.price > previous_price_history.price
            )  # True: Price went up; False: Price went down
            title_prefix = (
                "📉 Price Drop" if not has_price_increased else "📈 Price Increase"
            )
            embed_color = RED_COLOR if has_price_increased else GREEN_COLOR
            current_icon = "🟢" if not has_price_increased else "🔴"

        embeded_payload = [
            {
                "title": f"**{title_prefix}: [{item.name}]**",
                "url": item_url,
                "color": embed_color,
                "description": f"🌍 **Realm:** {region.upper()}"
                + f"-{current_price_history.server}",
                "thumbnail": {"url": icon_url},
                "fields": [
                    {
                        "name": "**Current Price**",
                        "value": f"```ansi\n{
                            Command._format_decimal_to_string(
                                current_price_history.price
                            )
                        } {current_icon}```",
                        "inline": False,
                    },
                    {
                        "name": "**Previous**",
                        "value": previous_price_text,
                        "inline": False,
                    },
                    {
                        "name": "**First Tracked**",
                        "value": first_price_text,
                        "inline": False,
                    },
                ],
            }
        ]

        return embeded_payload

    @staticmethod
    def _format_price_change(
        current_price: Decimal, compare_price: Decimal, is_first_price: bool = False
    ) -> str:
        """Prepares price text for a Discord embed.

        Args:
            current_price (Decimal): Current price.
            compare_price (Decimal): Either previous or first prices.
            is_first_price (bool, optional): True if it the first prices: False if it's
             not. Defaults to False.

        Returns:
            str: Formated price text.
        """
        price_diff = ((current_price - compare_price) / compare_price) * 100
        price_sign = "+" if price_diff > 0 else ""

        is_first_price_text = " overall" if is_first_price else ""

        if price_diff > 0:
            color_start, color_end = "\u001b[0;31m", "\u001b[0m"  # Red color
        elif price_diff < 0:
            color_start, color_end = "\u001b[0;32m", "\u001b[0m"  # Green color
        else:
            color_start, color_end = "", ""

        diff_text = (
            ""
            if price_diff == 0
            else f"({color_start}{price_sign}{price_diff:.1f}%{color_end}{
                is_first_price_text
            })"
        )

        return (
            f"```ansi\n{Command._format_decimal_to_string(compare_price)}"
            + f" {diff_text}```"
        )
