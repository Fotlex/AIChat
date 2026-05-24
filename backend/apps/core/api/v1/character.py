import base64

import orjson
from config.utils import fast_json
from django.db.models import F, Q

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation

SORT_CONFIG = {
    "recent": ("created_at", "id"),
    "popular": ("interaction_count", "id"),
}


@jwt_auth(methods=["GET"])
async def character_list_view(request):
    sort_key = request.GET.get("sort", "popular")
    gender = request.GET.get("gender")
    cursor_raw = request.GET.get("cursor")
    limit = 30

    sort_fields = SORT_CONFIG.get(sort_key, SORT_CONFIG["popular"])

    qs = Character.objects.filter(is_public=True)

    if gender in ("M", "F"):
        qs = qs.filter(gender=gender)

    if cursor_raw:
        try:
            cv = orjson.loads(base64.b64decode(cursor_raw))
            if len(cv) == 2:
                q_filter = Q(**{f"{sort_fields[0]}__lt": cv[0]}) | (
                    Q(**{sort_fields[0]: cv[0]}) & Q(**{f"{sort_fields[1]}__lt": cv[1]})
                )
                qs = qs.filter(q_filter)
        except Exception:
            pass

    order_by = [f"-{f}" for f in sort_fields]

    characters = [
        char
        async for char in qs.order_by(*order_by).values(
            "id",
            "name",
            "tagline",
            "user_story",
            "greeting_message",
            "author_id",
            author_name=F("author__username"),
            likes_count=F("interaction_count"),
            photo=F("avatar"),
        )[: limit + 1]
    ]

    has_more = len(characters) > limit
    next_cursor = None

    if has_more:
        characters.pop()
        last_item = characters[-1]
        next_vals = [
            last_item["likes_count"]
            if sort_key == "popular"
            else last_item["created_at"].isoformat(),
            last_item["id"],
        ]
        next_cursor = base64.b64encode(orjson.dumps(next_vals)).decode()

    if characters:
        char_ids = [c["id"] for c in characters]
        user_chats = {
            conv["character_id"]: str(conv["id"])
            async for conv in Conversation.objects.filter(
                user_id=request.user_id, character_id__in=char_ids
            ).values("character_id", "id")
        }

        for c in characters:
            if c["photo"]:
                c["photo"] = f"/media/{c['photo']}"
            c["chat_id"] = user_chats.get(c["id"])

    return fast_json({"items": characters, "next_cursor": next_cursor})
