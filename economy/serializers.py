from urllib.parse import urlparse

from rest_framework import serializers

from economy.models import Item


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField()  # Override to not trigger 50 length check
    display = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "display"]
        read_only_fields = ["name", "display"]

    def validate_id(self, value: str):
        item = value.strip()
        if not item:
            raise serializers.ValidationError("ID is empty.")

        if ItemSerializer._is_valid_id_format(item):
            return item

        parsed = urlparse(item)
        if "undermine.exchange" in parsed.netloc:
            path_segments = [seg for seg in parsed.fragment.split("/") if seg]
            if path_segments:
                potential_id = path_segments[-1]
                if ItemSerializer._is_valid_id_format(potential_id):
                    return potential_id

        raise serializers.ValidationError(
            "ID must be either in the format 12345"
            " or 12345-12, or be a link to an item."
        )

    @staticmethod
    def _is_valid_id_format(value: str) -> bool:
        """Checks whether a string matches the ID format: 12345 or 12345-12.

        Args:
            value (str): Value to verify.

        Returns:
            bool: True if a value matches the format; False otherwise.
        """
        parts = value.split("-")
        return len(parts) in (1, 2) and all(part.isdigit() for part in parts)
