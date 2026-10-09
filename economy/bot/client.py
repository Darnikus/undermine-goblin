# This example requires the 'message_content' intent.

import discord
from discord.ext import commands

from economy.bot.cogs.test import TestCog


class EconomyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        await self.add_cog(TestCog(bot=self))

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
