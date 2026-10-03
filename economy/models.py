from django.db import models


# Create your models here.
class Item(models.Model):
    id = models.IntegerField(primary_key=True, help_text="WoW in-game item ID")
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id})"
