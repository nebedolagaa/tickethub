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
        read_only_fields = ["id", "created_at", "slug"]


# Serializer for City-modellen
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


# Nikita Pushechnikov - Serializer for å opprette konsert
class ConcertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "venue",
            "title",
            "description",
            "performers",
            "start_datetime",
            "end_datetime",
            "slug",
        ]
        read_only_fields = ["id", "slug"]
        extra_kwargs = {
            "title": {"required": True},
            "organizer": {"required": True},
            "venue": {"required": True},
            "start_datetime": {"required": True},
            "end_datetime": {"required": True},
        }

    def validate(self, data):
        start = data.get("start_datetime")
        end = data.get("end_datetime")
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_datetime": "end_datetime må være etter start_datetime."}
            )
        return data

    def create(self, validated_data):
        validated_data["event_type"] = "concert"
        return super().create(validated_data)
