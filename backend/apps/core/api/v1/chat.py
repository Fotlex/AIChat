import orjson
from config.utils import R400, fast_json
from django.db.models import F
from django.utils import timezone

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation, LLMConfiguration, Message


@jwt_auth(methods=["GET"])
async def chat_list_view(request):
    chats = [
        chat
        async for chat in Conversation.objects.filter(user_id=request.user_id)
        .order_by("-last_activity_at")
        .values(
            "id",
            "last_message_preview",
            "last_activity_at",
            "character_id",
            character_name=F("character__name"),
            character_avatar=F("character__avatar"),
        )
    ]

    formatted_chats = []
    for c in chats:
        formatted_chats.append(
            {
                "id": str(c["id"]),
                "last_message": {"content": c["last_message_preview"]},
                "created_at": c["last_activity_at"].isoformat(),
                "character": {
                    "id": c["character_id"],
                    "name": c["character_name"],
                    "photo": f"/media/{c['character_avatar']}"
                    if c["character_avatar"]
                    else None,
                },
            }
        )

    return fast_json(formatted_chats)


@jwt_auth(methods=["GET"])
async def chat_messages_view(request, chat_id):
    cursor_raw = request.GET.get("cursor")
    cursor = int(cursor_raw) if cursor_raw and cursor_raw.isdigit() else 0
    limit = 30

    filters = {"conversation_id": chat_id}
    if cursor > 0:
        filters["id__lt"] = cursor

    messages = [
        msg
        async for msg in Message.objects.filter(**filters)
        .order_by("-id")
        .values("id", "role", "content", "created_at")[: limit + 1]
    ]

    next_cursor = None
    if len(messages) > limit:
        messages.pop()
        next_cursor = messages[-1]["id"]

    for m in messages:
        m["created_at"] = m["created_at"].isoformat()

    return fast_json({"items": messages, "next_cursor": next_cursor})


@jwt_auth(methods=["POST"])
async def message_send_view(request, character_id):
    try:
        payload = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        return R400

    content = payload.get("content", "").strip()[:1000]
    if not content:
        return R400

    now = timezone.now()

    conv = await Conversation.objects.filter(
        user_id=request.user_id, character_id=character_id
    ).afirst()

    created_messages = []

    if not conv:
        llm = await LLMConfiguration.objects.filter(is_active=True).afirst()
        char = (
            await Character.objects.filter(id=character_id)
            .values("greeting_message")
            .afirst()
        )

        conv = await Conversation.objects.acreate(
            user_id=request.user_id,
            character_id=character_id,
            llm_config_id=llm.id,
            last_message_preview=content,
            last_activity_at=now,
        )

        if char and char["greeting_message"]:
            created_messages.append(
                Message(
                    conversation=conv,
                    role=Message.RoleChoices.ASSISTANT,
                    content=char["greeting_message"],
                )
            )

    user_msg = Message(
        conversation=conv,
        role=Message.RoleChoices.USER,
        content=content,
        created_at=now,
    )
    created_messages.append(user_msg)

    await Message.objects.abulk_create(created_messages)

    if len(created_messages) == 1:
        await Conversation.objects.filter(id=conv.id).aupdate(
            last_message_preview=content, last_activity_at=now
        )

        await Character.objects.filter(id=character_id).aupdate(
            interaction_count=F("interaction_count") + 1
        )

    return fast_json({"id": user_msg.id, "chat_id": str(conv.id)}, status=201)
