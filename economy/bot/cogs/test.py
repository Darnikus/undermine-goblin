from discord.ext import commands


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! Latency: {round(self.bot.latency * 1000)}ms")

    @commands.command(name="echo")
    async def echo(self, ctx: commands.Context, *, text: str):
        await ctx.send(f"You said: {text}")
