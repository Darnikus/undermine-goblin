from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from economy.bot.client import EconomyBot


class Command(BaseCommand):
    help = "Starts the Discrod bot"

    def handle(self, *args: Any, **options: Any):
        if not settings.DISCORD_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR(
                    "DISCORD_BOT_TOKEN is missing in settings or .env file"
                )
            )

        self.stdout.write(self.style.SUCCESS("Starting Discord bot..."))

        client = EconomyBot()
        client.run(settings.DISCORD_BOT_TOKEN)
