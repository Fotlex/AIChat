import orjson
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Chat, Message
from .tasks import generate_ai_response_task


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chats = list(
            Chat.objects.filter(user_id=request.user.telegram_id).values(
                "id",
                "last_message_text",
                "last_message_at",
                "character_id",
                "character__name",
                "character__photo",
                "character__description",
            )
        )
        return HttpResponse(orjson.dumps(chats), content_type="application/json")


class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        limit = 30

        query = Message.objects.filter(
            chat_id=chat_id, chat__user_id=request.user.telegram_id
        )

        cursor = request.query_params.get("cursor")
        if cursor:
            query = query.filter(id__lt=int(cursor))

        messages = list(
            query.order_by("-id")[: limit + 1].values(
                "id", "role", "content", "created_at"
            )
        )

        has_more = len(messages) > limit
        next_cursor = None

        if has_more:
            messages.pop()
            next_cursor = messages[-1]["id"]

        messages.reverse()

        return HttpResponse(
            orjson.dumps(
                {
                    "items": messages,
                    "next_cursor": next_cursor,
                }
            ),
            content_type="application/json",
        )


class MessageSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, character_id):
        content = request.data.get("content")
        if not content or not isinstance(content, str):
            return HttpResponse(
                orjson.dumps({"error": "Content required"}),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        content = content.strip()[:1000]
        now = timezone.now()
        user_id = request.user.telegram_id

        chat_id = (
            Chat.objects.filter(user_id=user_id, character_id=character_id)
            .values_list("id", flat=True)
            .first()
        )

        with transaction.atomic():
            if chat_id:
                last_msg = Message.objects.create(
                    chat_id=chat_id,
                    role=Message.Role.USER,
                    content=content,
                    created_at=now,
                )
            else:
                chat, created = Chat.objects.get_or_create(
                    user_id=user_id, character_id=character_id
                )
                chat_id = chat.id

                if not created:
                    last_msg = Message.objects.create(
                        chat_id=chat_id,
                        role=Message.Role.USER,
                        content=content,
                        created_at=now,
                    )
                else:
                    from apps.characters.models import Character

                    welcome_text = (
                        Character.objects.filter(id=character_id)
                        .values_list("welcome_message", flat=True)
                        .first()
                    )

                    msgs = []
                    if welcome_text:
                        msgs.append(
                            Message(
                                chat=chat,
                                role=Message.Role.ASSISTANT,
                                content=welcome_text,
                                created_at=now,
                            )
                        )

                    msgs.append(
                        Message(
                            chat=chat,
                            role=Message.Role.USER,
                            content=content,
                            created_at=now,
                        )
                    )

                    created_msgs = Message.objects.bulk_create(msgs)
                    last_msg = created_msgs[-1]

            Chat.objects.filter(id=chat_id).update(
                last_message_text=content, last_message_at=now
            )

            transaction.on_commit(
                lambda: generate_ai_response_task.delay(chat_id, user_id)
            )

        return HttpResponse(
            orjson.dumps({"id": last_msg.id, "chat_id": chat_id}),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
