from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model=Event
        fields=[
            'id', 'organizer', 'venue', 'title', 'description', 'performers',
            'event_type', 'start_datetime', 'end_datetime', 'is_archived', 'slug'
        ]   
        read_only_fields= ['id', 'created_at', 'slug']    