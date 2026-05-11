from rest_framework import serializers

from .models import BotData


class BotDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotData
        fields = ['id', 'bot_name', 'payload', 'created_at']
        read_only_fields = ['id', 'created_at']
