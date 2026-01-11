from django.db import transaction
from django.db.models import OuterRef, Subquery
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.characters.models import Character

from .models import Chat, Message
from .pagination import MessageCursorPagination
from .serializers import (
    ChatDetailSerializer,
    ChatListSerializer,
    MessageSerializer,
)
from .tasks import generate_ai_response_task


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = MessageCursorPagination

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            newest_msg = Message.objects.filter(chat=OuterRef("pk")).order_by(
                "-created_at"
            )

            return (
                Chat.objects.filter(user=user)
                .select_related("character")
                .annotate(
                    last_message_content=Subquery(newest_msg.values("content")[:1]),
                    last_message_role=Subquery(newest_msg.values("role")[:1]),
                    last_message_created_at=Subquery(
                        newest_msg.values("created_at")[:1]
                    ),
                )
                .order_by("-created_at")
            )
        return Chat.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        if self.action in ["messages", "get_or_create_chat", "send_message"]:
            return MessageSerializer
        return ChatDetailSerializer

    @action(
        detail=False, methods=["get"], url_path="character/(?P<character_id>[^/.]+)"
    )
    def get_or_create_chat(self, request, character_id=None):
        character = get_object_or_404(Character, pk=character_id)

        with transaction.atomic():
            chat, created = Chat.objects.get_or_create(
                user=request.user, character=character
            )
            if created and character.welcome_message:
                Message.objects.create(
                    chat=chat,
                    role=Message.Role.ASSISTANT,
                    content=character.welcome_message,
                )

        messages_queryset = chat.messages.all().order_by("-created_at")
        paginated_messages = self.paginate_queryset(messages_queryset)
        messages_serializer = self.get_serializer(paginated_messages, many=True)

        chat_serializer = ChatDetailSerializer(chat)

        paginated_response = self.get_paginated_response(messages_serializer.data)
        paginated_response.data["chat"] = chat_serializer.data
        return paginated_response

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        chat = self.get_object()
        queryset = chat.messages.all().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Content required"}, status=400)

        with transaction.atomic():
            user_message = Message.objects.create(
                chat=chat, role=Message.Role.USER, content=content
            )
            transaction.on_commit(
                lambda: generate_ai_response_task.delay(
                    chat_id=chat.id, user_telegram_id=request.user.telegram_id
                )
            )

        return Response(
            MessageSerializer(user_message).data, status=status.HTTP_201_CREATED
        )
