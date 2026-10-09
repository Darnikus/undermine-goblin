import discord
from discord import app_commands
from discord.ext import commands


class ItemCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="add", description="Add an item by URL or ID")
    @app_commands.describe(item="Past the Undermine.exchange URL or raw Item ID")
    async def add_item(self, interaction: discord.Interaction, item: str):
        # TODO do the method
        await interaction.response.defer(thinking=True)

        await interaction.followup.send(f"Successfully tracking item ID: `{item}`")
