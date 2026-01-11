from rest_framework import serializers

from apps.characters.serializers import CharacterListSerializer

from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]


class ChatListSerializer(serializers.ModelSerializer):
    character = CharacterListSerializer(read_only=True)
    last_message_content = serializers.CharField(read_only=True)
    last_message_role = serializers.CharField(read_only=True)
    last_message_created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Chat
        fields = [
            "id",
            "character",
            "created_at",
            "last_message_content",
            "last_message_role",
            "last_message_created_at",
        ]


class ChatDetailSerializer(serializers.ModelSerializer):
    character = CharacterListSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "character"]
