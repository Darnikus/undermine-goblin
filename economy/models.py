from django.db import models


# Create your models here.
class Item(models.Model):
    id = models.IntegerField(primary_key=True, help_text="WoW in-game item ID")
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id})"


class PriceHistory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    server = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
