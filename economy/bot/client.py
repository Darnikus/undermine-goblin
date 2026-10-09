# This example requires the 'message_content' intent.

import discord
from discord.ext import commands


class EconomyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:

        @self.command(name="ping")
        async def ping(ctx: commands.Context):
            await ctx.send(f"Pong! Latency: {round(self.latency * 1000)}ms")

        @self.command(name="echo")
        async def echo(ctx: commands.Context, *, text: str):
            await ctx.send(f"You said: {text}")

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
