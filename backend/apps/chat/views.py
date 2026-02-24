import orjson
from asgiref.sync import sync_to_async
from config.utils import R400, R404, fast_json
from django.db import transaction
from django.utils import timezone

from apps.characters.models import Character
from apps.chat.models import Chat, Message
from apps.chat.tasks import generate_ai_response_task
from apps.users.auth import twa_auth


@twa_auth("GET")
async def chat_list_view(request):
    chats = await sync_to_async(list)(
        Chat.objects.filter(user_id=request.user.telegram_id)
        .order_by("-last_message_at")
        .values(
            "id",
            "last_message_text",
            "last_message_at",
            "character_id",
            "character__name",
            "character__photo",
            "character__description",
        )
    )
    return fast_json(chats)


@twa_auth("GET")
async def chat_detail_view(request, chat_id):
    if not await Chat.objects.filter(
        id=chat_id, user_id=request.user.telegram_id
    ).aexists():
        return R404

    cursor_raw = request.GET.get("cursor")
    cursor = int(cursor_raw) if cursor_raw and cursor_raw.isdigit() else 0

    filters = {"chat_id": chat_id}
    if cursor > 0:
        filters["id__lt"] = cursor

    limit = 30
    messages = await sync_to_async(list)(
        Message.objects.filter(**filters)
        .order_by("-id")
        .values("id", "role", "content", "created_at")[: limit + 1]
    )

    next_cursor = None
    if len(messages) > limit:
        messages.pop()
        next_cursor = messages[-1]["id"]

    return fast_json({"items": messages, "next_cursor": next_cursor})


@twa_auth("POST")
async def message_send_view(request, character_id):
    try:
        payload = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        return R400

    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        return R400

    content = content.strip()[:1000]

    result = await sync_to_async(_sync_save_message)(
        request.user.telegram_id, character_id, content
    )
    return fast_json(result, status=201)


def _sync_save_message(user_id, character_id, content):
    now = timezone.now()
    with transaction.atomic():
        chat = (
            Chat.objects.select_for_update()
            .filter(user_id=user_id, character_id=character_id)
            .first()
        )

        to_create = []
        created = False

        if not chat:
            chat, created = Chat.objects.get_or_create(
                user_id=user_id,
                character_id=character_id,
                defaults={"last_message_text": content, "last_message_at": now},
            )

            if created:
                welcome = (
                    Character.objects.filter(id=character_id)
                    .values_list("welcome_message", flat=True)
                    .first()
                )
                if welcome:
                    to_create.append(
                        Message(
                            chat=chat, role="assistant", content=welcome, created_at=now
                        )
                    )

        user_msg = Message(chat=chat, role="user", content=content, created_at=now)
        to_create.append(user_msg)
        Message.objects.bulk_create(to_create)

        if not created:
            Chat.objects.filter(id=chat.id).update(
                last_message_text=content, last_message_at=now
            )

        transaction.on_commit(lambda: generate_ai_response_task.delay(chat.id, user_id))

        return {"id": user_msg.id, "chat_id": chat.id}
