import base64

import orjson
from config.utils import R400, fast_json
from django.db.models import F, Q
from django.utils import timezone

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation, LLMConfiguration, Message


@jwt_auth(methods=["GET"])
async def chat_list_view(request):
    cursor_raw = request.GET.get("cursor")
    limit = 30

    qs = Conversation.objects.filter(user_id=request.user_id)

    if cursor_raw:
        try:
            cv = orjson.loads(base64.b64decode(cursor_raw))
            if len(cv) == 2:
                q_filter = Q(last_activity_at__lt=cv[0]) | (
                    Q(last_activity_at=cv[0]) & Q(id__lt=cv[1])
                )
                qs = qs.filter(q_filter)
        except Exception:
            pass

    chats = [
        chat
        async for chat in qs.order_by("-last_activity_at", "-id").values(
            "id",
            "last_message_preview",
            "last_activity_at",
            "character_id",
            character_name=F("character__name"),
            character_avatar=F("character__avatar"),
        )[: limit + 1]
    ]

    has_more = len(chats) > limit
    next_cursor = None

    if has_more:
        chats.pop()
        last_item = chats[-1]
        next_vals = [last_item["last_activity_at"].isoformat(), str(last_item["id"])]
        next_cursor = base64.b64encode(orjson.dumps(next_vals)).decode()

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

    return fast_json({"items": formatted_chats, "next_cursor": next_cursor})


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
        if not llm:
            return fast_json({"error": "LLM not configured in admin"}, status=500)

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

    ai_text = f"✨ [Нейросеть]: Я получила твое сообщение: «{content[:30]}...»"
    ai_msg = Message(
        conversation=conv,
        role=Message.RoleChoices.ASSISTANT,
        content=ai_text,
        created_at=now,
    )
    created_messages.append(ai_msg)

    await Message.objects.abulk_create(created_messages)

    await Conversation.objects.filter(id=conv.id).aupdate(
        last_message_preview=ai_text, last_activity_at=now
    )

    return fast_json(
        {
            "id": user_msg.id,
            "chat_id": str(conv.id),
            "ai_message": {
                "id": ai_msg.id,
                "role": ai_msg.role,
                "content": ai_text,
                "created_at": ai_msg.created_at.isoformat(),
            },
        },
        status=201,
    )
