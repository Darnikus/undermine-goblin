from typing import Any

from bot.config import DISCORD_BOT_TOKEN
from django.core.management.base import BaseCommand

from economy.bot.client import EconomyBot


class Command(BaseCommand):
    help = "Starts the Discrod bot"

    def handle(self, *args: Any, **options: Any):
        if not DISCORD_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR("DISCORD_BOT_TOKEN is missing in .env file")
            )
            return

        self.stdout.write(self.style.SUCCESS("Starting Discord bot..."))

        client = EconomyBot()
        client.run(DISCORD_BOT_TOKEN)
