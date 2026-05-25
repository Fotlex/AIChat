import base64

import orjson
from config.utils import fast_json
from django.db.models import Exists, F, OuterRef, Q

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation
from apps.core.models.character import FavoriteCharacter

SORT_CONFIG = {
    "recent": ("created_at", "id"),
    "popular": ("interaction_count", "id"),
}


@jwt_auth(methods=["GET"])
async def character_list_view(request):
    sort_key = request.GET.get("sort", "popular")
    tab = request.GET.get("tab", "all")
    cursor_raw = request.GET.get("cursor")
    limit = 30

    sort_fields = SORT_CONFIG.get(sort_key, SORT_CONFIG["popular"])
    qs = Character.objects.filter(is_public=True)

    if tab == "favorites":
        qs = qs.filter(favoritecharacter__user_id=request.user_id)

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

    is_fav_subquery = FavoriteCharacter.objects.filter(
        user_id=request.user_id, character_id=OuterRef("id")
    )

    characters = [
        char
        async for char in qs.order_by(*order_by)
        .annotate(is_favorite=Exists(is_fav_subquery))
        .values(
            "id",
            "name",
            "tagline",
            "user_story",
            "greeting_message",
            "author_id",
            "created_at",
            author_name=F("author__username"),
            likes_count=F("interaction_count"),
            photo=F("avatar"),
            is_fav=F("is_favorite"),
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
            c["is_favorite"] = c.pop("is_fav")

    return fast_json({"items": characters, "next_cursor": next_cursor})


@jwt_auth(methods=["POST"])
async def toggle_favorite_view(request, character_id):
    deleted_count, _ = await FavoriteCharacter.objects.filter(
        user_id=request.user_id, character_id=character_id
    ).adelete()

    if deleted_count > 0:
        await Character.objects.filter(id=character_id).aupdate(
            interaction_count=F("interaction_count") - 1
        )
        return fast_json({"status": "unliked"})
    else:
        await FavoriteCharacter.objects.acreate(
            user_id=request.user_id, character_id=character_id
        )
        await Character.objects.filter(id=character_id).aupdate(
            interaction_count=F("interaction_count") + 1
        )
        return fast_json({"status": "liked"})
