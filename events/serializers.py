from rest_framework import serializers
from .models import Event, City


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "venue",
            "title",
            "description",
            "performers",
            "event_type",
            "start_datetime",
            "end_datetime",
            "is_archived",
            "slug",
        ]
        # arrangør settes fra innlogget bruker og kan ikke endres via API-et
        read_only_fields = ["id", "created_at", "slug", "organizer"]


# Serializer for City-modellen
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


# Nikita Pushechnikov - Serializer for å opprette event
class EventCreateSerializer(serializers.ModelSerializer):
    VALID_EVENT_TYPES = ["concert", "festival"]

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "venue",
            "title",
            "description",
            "performers",
            "event_type",
            "start_datetime",
            "end_datetime",
            "slug",
        ]
        # arrangør settes fra innlogget bruker i viewet, ikke fra request body
        read_only_fields = ["id", "slug", "organizer"]
        extra_kwargs = {
            "title": {"required": True},
            "venue": {"required": True},
            "start_datetime": {"required": True},
            "end_datetime": {"required": True},
            "event_type": {"required": False},
        }

    def validate_event_type(self, value):
        if value not in self.VALID_EVENT_TYPES:
            raise serializers.ValidationError(
                f"Ugyldig event_type. Velg mellom: {', '.join(self.VALID_EVENT_TYPES)}."
            )
        return value

    def validate(self, data):
        start = data.get("start_datetime")
        end = data.get("end_datetime")
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_datetime": "end_datetime må være etter start_datetime."}
            )
        return data

    def create(self, validated_data):
        validated_data.setdefault("event_type", "concert")
        return super().create(validated_data)
