from rest_framework import serializers

from backend.characters.serializers import CharacterListSerializer

from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]


class ChatListSerializer(serializers.ModelSerializer):
    character = CharacterListSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "character", "last_message", "created_at"]

    def get_last_message(self, obj: Chat) -> dict | None:
        last_msg = obj.messages.order_by("-created_at").first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None


class ChatDetailSerializer(serializers.ModelSerializer):
    character = CharacterListSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "character"]
