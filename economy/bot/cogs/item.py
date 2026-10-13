from urllib.parse import urlparse

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands

from config import settings
from economy.models import Item
from economy.scraper import Region


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

    @app_commands.command(name="delete", description="Delete the item")
    @app_commands.describe(item_id="Raw Item ID")
    async def delete_item(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.send_message(f"You deleted item with id {item_id}")

    @delete_item.autocomplete("item_id")
    async def delete_item_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        item_ids = await sync_to_async(list)(
            Item.objects.all().values_list("id", flat=True)
        )

        return [
            app_commands.Choice(name=str(id), value=str(id))
            for id in item_ids
            if current in str(id)
        ]

    @app_commands.command(
        name="list",
        description="Display all items currently being tracked"
        + " from Undermine.exchange.",
    )
    async def list_items(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        region = Region[getattr(settings, "REGION", "EU")]
        items = await sync_to_async(list)(Item.objects.all())

        if not items:
            await interaction.followup.send("No items are currently being tracked.")
            return

        embed = discord.Embed(
            title="📋 Tracked Items",
            description="Here is the current list of monitored items.",
            color=discord.Color.blue(),
        )

        for item in items:
            name = item.name or "*(Pending Scrape...)*"
            embed.add_field(
                name=f"(ID: {item.id})",
                value=f"**Name:** [{name}](https://undermine.exchange/{region.value}/{item.id})",
                inline=False,
            )

        embed.set_footer(text=f"Total items: {len(items)}")
        await interaction.followup.send(embed=embed, ephemeral=True)

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
