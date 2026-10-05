from django.contrib import admin

from economy.models import Item, PriceHistory


# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", "id")


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("item", "server", "price", "timestamp")
    list_filter = ("server",)
    search_fields = ("item__name",)
