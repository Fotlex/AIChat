# backend/chats/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.characters.models import Character

from .models import Chat, Message
from .pagination import MessageCursorPagination
from .serializers import (
    ChatDetailSerializer,
    ChatListSerializer,
    MessageSerializer,
)


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = MessageCursorPagination

    @property
    def paginator(self):
        if self.action == "list":
            return None
        return super().paginator

    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        if self.action in ["messages", "get_or_create_chat"]:
            return MessageSerializer
        return ChatDetailSerializer

    def get_queryset(self):
        if self.action == "list":
            return (
                Chat.objects.filter(user=self.request.user)
                .prefetch_related("character", "messages")
                .order_by("-created_at")
            )
        return Chat.objects.filter(user=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        url_path="character/(?P<character_id>[^/.]+)",
        url_name="character-chat",
    )
    def get_or_create_chat(self, request, character_id=None):
        character = get_object_or_404(Character, pk=character_id)
        chat, created = Chat.objects.get_or_create(
            user=request.user, character=character
        )
        if created and character.welcome_message:
            Message.objects.create(
                chat=chat,
                role=Message.Role.ASSISTANT,
                content=character.welcome_message,
            )

        messages_queryset = chat.messages.all()
        paginated_messages = self.paginate_queryset(messages_queryset)
        messages_serializer = self.get_serializer(paginated_messages, many=True)
        chat_serializer = ChatDetailSerializer(chat)

        paginated_response = self.get_paginated_response(messages_serializer.data)
        paginated_response.data["chat"] = chat_serializer.data
        return paginated_response

    @action(detail=True, methods=["get"], url_path="messages", url_name="messages-list")
    def messages(self, request, pk=None):
        chat = self.get_object()
        queryset = chat.messages.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
