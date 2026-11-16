from rest_framework import serializers

from economy.models import Item


class ItemSerializer(serializers.ModelSerializer):
    display = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "display"]
        read_only_fields = ["name", "display"]
