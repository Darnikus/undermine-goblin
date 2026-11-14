from rest_framework import serializers

from economy.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name"]
        read_only_fields = ["name"]
