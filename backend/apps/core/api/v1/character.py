import base64
import logging
import uuid

import orjson
from asgiref.sync import sync_to_async
from config.utils import fast_json
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Exists, F, OuterRef, Q

from apps.core.decorators import jwt_auth
from apps.core.models import Character, Conversation, User
from apps.core.models.character import FavoriteCharacter

SORT_CONFIG = {
    "recent": ("created_at", "id"),
    "popular": ("interaction_count", "id"),
}

logger = logging.getLogger(__name__)


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


def _create_character_sync_transaction(
    user_id, name, tagline, system_prompt, greeting_message, avatar_b64
):
    with transaction.atomic():
        user = User.objects.select_for_update().get(id=user_id)

        PUBLISH_COST = 100
        if user.balance < PUBLISH_COST:
            raise ValueError("Недостаточно кристаллов для создания (нужно 100 💎)")

        user.balance -= PUBLISH_COST
        user.save()

        char = Character(
            name=name[:128],
            tagline=tagline[:255],
            system_prompt=system_prompt,
            greeting_message=greeting_message,
            author_id=user_id,
            is_public=True,
        )

        if avatar_b64 and ";base64," in avatar_b64:
            format_str, imgstr = avatar_b64.split(";base64,")
            ext = format_str.split("/")[-1]
            img_data = base64.b64decode(imgstr)
            char.avatar.save(
                f"avatar_{uuid.uuid4().hex[:8]}.{ext}",
                ContentFile(img_data),
                save=False,
            )

        char.save()
        return char.id, user.balance


create_character_in_db = sync_to_async(_create_character_sync_transaction)


@jwt_auth(methods=["POST"])
async def create_character_view(request):
    try:
        data = orjson.loads(request.body)
        name = data.get("name", "").strip()
        tagline = data.get("tagline", "").strip()
        system_prompt = data.get("system_prompt", "").strip()
        greeting_message = data.get("greeting_message", "").strip()
        avatar_b64 = data.get("avatar")

        if not name or not system_prompt:
            return fast_json(
                {"error": "Имя и системный промпт обязательны"}, status=400
            )

        try:
            char_id, new_balance = await create_character_in_db(
                request.user_id,
                name,
                tagline,
                system_prompt,
                greeting_message,
                avatar_b64,
            )
        except ValueError as e:
            return fast_json({"error": str(e)}, status=400)

        return fast_json(
            {"status": "ok", "id": char_id, "new_balance": new_balance}, status=201
        )

    except Exception as e:
        logger.error(
            "Ошибка при создании персонажа в представлении: %s", str(e), exc_info=True
        )
        return fast_json({"error": "Ошибка при создании персонажа"}, status=400)


@jwt_auth(methods=["GET"])
async def character_detail_view(request, character_id):
    char = (
        await Character.objects.filter(id=character_id)
        .values(
            "id",
            "name",
            "gender",
            "tagline",
            "user_story",
            "greeting_message",
            "avatar",
            "author_id",
            "interaction_count",
            "is_public",
            "created_at",
            author_name=F("author__username"),
        )
        .afirst()
    )

    if not char:
        return fast_json({"error": "Не найден"}, status=404)

    if not char["is_public"] and char["author_id"] != request.user_id:
        return fast_json({"error": "Доступ запрещен"}, status=403)

    if char["avatar"]:
        char["photo"] = f"/media/{char['avatar']}"
    else:
        char["photo"] = None

    char["likes_count"] = char.pop("interaction_count")

    is_fav = await FavoriteCharacter.objects.filter(
        user_id=request.user_id, character_id=character_id
    ).aexists()
    char["is_favorite"] = is_fav

    conv = (
        await Conversation.objects.filter(
            user_id=request.user_id, character_id=character_id
        )
        .values("id")
        .afirst()
    )
    char["chat_id"] = str(conv["id"]) if conv else None

    return fast_json(char)
