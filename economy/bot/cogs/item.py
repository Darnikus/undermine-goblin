from urllib.parse import urlparse

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands

from config import settings
from economy.models import Item
from economy.scraper import Region
from economy.services.graphs import generate_price_graph


class ItemCog(commands.GroupCog, group_name="item"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def item_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Helper method for item autocomplete.

        Args:
            interaction (discord.Interaction): An interaction from a user.
            current (str): Current item choice.

        Returns:
            list[app_commands.Choice[str]]: Item choices.
        """
        items = await sync_to_async(list)(Item.objects.all())

        return [
            app_commands.Choice(name=item.__str__(), value=str(item.id))
            for item in items
            if current in str(item.id)
        ]

    @app_commands.command(name="add", description="Add an item by URL or ID")
    @app_commands.describe(item="Past the Undermine.exchange URL or raw Item ID")
    async def add_item(self, interaction: discord.Interaction, item: str):
        """Discord command to delete an item.

        Args:
            interaction (discord.Interaction): An interaction from a user.
            item (str): An item's ID or a full item's URL.
        """
        await interaction.response.defer(thinking=True)

        item_id = self._parse_item_input(item)
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
    @app_commands.autocomplete(item_id=item_autocomplete)
    async def delete_item(self, interaction: discord.Interaction, item_id: str):
        """Discord command to delete an item.

        Args:
            interaction (discord.Interaction): An interaction from a user.
            item_id (str): An item's ID.
        """
        await interaction.response.defer(thinking=True)

        try:
            item = await sync_to_async(Item.objects.get)(id=item_id)
            display_text = item.__str__()
            await sync_to_async(item.delete)()

            await interaction.followup.send(
                f"✅ Successfully deleted `{display_text}`.", ephemeral=True
            )

        except Item.DoesNotExist:
            await interaction.followup.send(
                f"⚠️ Item with ID: `{item_id}` was not found.", ephemeral=True
            )
        except Exception:
            await interaction.followup.send(
                "❌ An error occurred while deleting the item.", ephemeral=True
            )

    @app_commands.command(
        name="list",
        description="Display all items currently being tracked"
        + " from Undermine.exchange.",
    )
    async def list_items(self, interaction: discord.Interaction):
        """Discord command to list all items.

        Args:
            interaction (discord.Interaction): An interaction from a user.
        """
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

    @app_commands.command(
        name="pricegraph", description="Show a price history graph for an item."
    )
    @app_commands.describe(item_id="Raw Item ID")
    @app_commands.autocomplete(item_id=item_autocomplete)
    async def pricegraph(self, interaction: discord.Interaction, item_id: str):
        """Discord command to build an item's price graph.

        Args:
            interaction (discord.Interaction): An interaction from a user.
            item_id (str): An item's ID.
        """
        await interaction.response.defer(thinking=True)
        try:
            item = await sync_to_async(Item.objects.get)(id=item_id)
            prices = await sync_to_async(list)(item.prices.all())

            buffer = await generate_price_graph(prices)
            file = discord.File(buffer, filename="price_history.png")
            embed = discord.Embed(
                title="📈 Price History Graph", color=discord.Color.blurple()
            )
            embed.set_image(url="attachment://price_history.png")

            await interaction.followup.send(embed=embed, file=file)

        except Item.DoesNotExist:
            await interaction.followup.send(
                f"⚠️ Item with ID: `{item_id}` was not found.", ephemeral=True
            )
        except Exception:
            pass

    @staticmethod
    def _parse_item_input(item: str) -> str | None:
        """Parses the user's item input.

        Args:
            item (str): Probably an item's ID or URL.

        Returns:
            str | None: An item's ID, or None if the input is invalid.
        """
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
