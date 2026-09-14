import base64

import orjson
from config.utils import R400, fast_json
from django.conf import settings
from django.db.models import F, Q
from django.http import StreamingHttpResponse
from django.utils import timezone
from openai import AsyncOpenAI

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation, LLMConfiguration, Message, User


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

    filters = {"conversation_id": chat_id, "conversation__user_id": request.user_id}
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


aclient = AsyncOpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.HF_TOKEN,
)


@jwt_auth(methods=["POST"])
async def message_send_view(request, character_id):
    try:
        payload = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        return R400

    content = payload.get("content", "").strip()[:1000]
    if not content:
        return R400

    user = await User.objects.select_related("preferred_llm").aget(id=request.user_id)
    llm = user.preferred_llm
    if not llm:
        llm = await LLMConfiguration.objects.filter(is_active=True).afirst()

    if not llm:
        return fast_json({"error": "Нет доступных моделей"}, status=400)

    if user.balance < llm.cost_per_request:
        return fast_json({"error": "Недостаточно кристаллов 💎"}, status=402)

    now = timezone.now()
    char = await Character.objects.aget(id=character_id)
    conv = await Conversation.objects.filter(
        user_id=request.user_id, character_id=character_id
    ).afirst()

    created_messages = []

    if not conv:
        conv = await Conversation.objects.acreate(
            user_id=request.user_id,
            character_id=character_id,
            llm_config_id=llm.id,
            last_activity_at=now,
        )
        if char.greeting_message:
            created_messages.append(
                Message(
                    conversation=conv,
                    role=Message.RoleChoices.ASSISTANT,
                    content=char.greeting_message,
                )
            )

    user_msg = Message(
        conversation=conv,
        role=Message.RoleChoices.USER,
        content=content,
        created_at=now,
    )
    ai_msg = Message(
        conversation=conv,
        role=Message.RoleChoices.ASSISTANT,
        content="",
        created_at=now,
    )
    created_messages.extend([user_msg, ai_msg])
    await Message.objects.abulk_create(created_messages)

    history = [
        msg
        async for msg in Message.objects.filter(conversation=conv).order_by("-id")[:10]
    ]
    history.reverse()

    system_prompt = (
        f"{char.system_prompt}\n\n"
        "ВАЖНОЕ ПРАВИЛО: Ты общаешься строго на РУССКОМ языке. "
        "Никогда не признавайся, что ты ИИ, языковая модель или программа. "
        "Отыгрывай своего персонажа на 100%, используй его манеру речи."
    )

    api_messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        if h.content:
            api_messages.append({"role": h.role, "content": h.content})

    async def event_stream():
        full_text = ""
        try:
            init_data = {
                "type": "init",
                "user_msg": {"id": user_msg.id, "content": user_msg.content},
                "ai_msg_id": ai_msg.id,
                "chat_id": str(conv.id),
            }
            yield f"data: {orjson.dumps(init_data).decode()}\n\n"

            stream = await aclient.chat.completions.create(
                model=llm.provider_code,
                messages=api_messages,
                stream=True,
                max_tokens=800,
                temperature=0.7,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text_chunk = chunk.choices[0].delta.content
                    full_text += text_chunk
                    yield f"data: {orjson.dumps({'type': 'chunk', 'text': text_chunk}).decode()}\n\n"

            if full_text:
                await Message.objects.filter(id=ai_msg.id).aupdate(content=full_text)
                await Conversation.objects.filter(id=conv.id).aupdate(
                    last_message_preview=full_text[:100],
                    last_activity_at=timezone.now(),
                )
                await User.objects.filter(id=user.id).aupdate(
                    balance=F("balance") - llm.cost_per_request
                )

            yield f"data: {orjson.dumps({'type': 'done'}).decode()}\n\n"

        except Exception as e:
            yield f"data: {orjson.dumps({'type': 'error', 'message': str(e)}).decode()}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    return response
