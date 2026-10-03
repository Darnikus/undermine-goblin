from django.contrib import admin

from economy.models import Item


# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", "id")
