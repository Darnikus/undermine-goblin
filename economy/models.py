from typing import TYPE_CHECKING

from django.db import models


# Create your models here.
class Item(models.Model):
    id = models.IntegerField(primary_key=True, help_text="WoW in-game item ID")
    name = models.CharField(max_length=255)

    if TYPE_CHECKING:
        prices: models.Manager[PriceHistory]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id})"


class PriceHistory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="prices")
    server = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Ensures `item.prices.all()` is automatically sorted from oldest to newest."""

        ordering = ["timestamp"]
