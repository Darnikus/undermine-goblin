from urllib.parse import urlparse

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands

from economy.models import Item


class ItemCog(commands.GroupCog, group_name="item"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="add", description="Add an item by URL or ID")
    @app_commands.describe(item="Past the Undermine.exchange URL or raw Item ID")
    async def add_item(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer(thinking=True)

        item_id = self.parse_item_input(item)
        if not item_id:
            await interaction.followup.send(
                "❌ Invalid format! Please provide a valid URL or an Item ID.",
                ephemeral=True,
            )
            return

        try:
            tracked_item, created = await sync_to_async(Item.objects.get_or_create)(
                id=int(item_id)
            )

            if created:
                await interaction.followup.send(
                    f"✅ Successfully added item `{tracked_item.id}`"
                    + " to your tracking list!"
                    + " *Details will sync in the next update cycle.*",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    f"⚠️ You are already tracking item `{tracked_item.id}`.",
                    ephemeral=True,
                )
        except Exception:
            await interaction.followup.send(
                "❌ An error occurred while saving to the database.", ephemeral=True
            )

    @staticmethod
    def parse_item_input(item: str) -> str | None:
        item = item.strip()
        if not item:
            return None

        if item.isdigit():
            return item

        parsed = urlparse(item)
        if "undermine.exchange" in parsed.netloc:
            path_segments = [seg for seg in parsed.fragment.split("/") if seg]
            if path_segments:
                potential_id = path_segments[-1]
                if potential_id.isdigit():
                    return potential_id

        return None
