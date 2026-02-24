import base64
import binascii

import orjson
from asgiref.sync import sync_to_async
from config.utils import R204, R400, fast_json
from django.db.models import Exists, F, IntegerField, OuterRef, Q, Subquery

from apps.chat.models import Chat
from apps.users.auth import twa_auth

from .models import Character, CharacterLike

SORT_CONFIG = {
    "recent": ("id",),
    "popular": ("likes_count", "id"),
}


@twa_auth("GET")
async def character_list_view(request):
    params = request.GET
    limit = 30
    user_id = request.user.telegram_id

    def get_characters_sync():
        queryset = Character.objects.filter(is_active=True)

        is_yours = params.get("yours")
        if is_yours == "1":
            queryset = queryset.filter(creator_id=user_id)
        elif is_yours == "0":
            queryset = queryset.exclude(creator_id=user_id)

        gender = params.get("gender")
        if gender in ("M", "F"):
            queryset = queryset.filter(gender=gender)

        sort_key = params.get("sort", "recent")
        sort_fields = SORT_CONFIG.get(sort_key, SORT_CONFIG["recent"])

        cursor_raw = params.get("cursor")
        if cursor_raw:
            try:
                cv = orjson.loads(base64.b64decode(cursor_raw))
                if len(cv) == len(sort_fields):
                    pagination_filter = Q()
                    for i in range(len(sort_fields)):
                        q_part = Q(**{f"{sort_fields[i]}__lt": cv[i]})
                        for j in range(i):
                            q_part &= Q(**{sort_fields[j]: cv[j]})
                        pagination_filter |= q_part
                    queryset = queryset.filter(pagination_filter)
            except (ValueError, TypeError, binascii.Error, orjson.JSONDecodeError):
                pass

        chat_id_subquery = Chat.objects.filter(
            user_id=user_id, character=OuterRef("pk")
        ).values("id")[:1]

        is_liked_exists = CharacterLike.objects.filter(
            user_id=user_id, character=OuterRef("pk")
        )

        queryset = queryset.annotate(
            chat_id=Subquery(chat_id_subquery, output_field=IntegerField()),
            is_liked=Exists(is_liked_exists),
        )

        order_by = [f"-{f}" for f in sort_fields]

        return list(
            queryset.order_by(*order_by)[: limit + 1].values(
                "id",
                "name",
                "gender",
                "description",
                "photo",
                "likes_count",
                "welcome_message",
                "chat_id",
                "is_liked",
                *sort_fields,
            )
        ), sort_fields

    characters, sort_fields = await sync_to_async(get_characters_sync)()

    has_more = len(characters) > limit
    next_cursor = None

    if has_more:
        characters.pop()
        last_item = characters[-1]
        next_vals = [last_item[f] for f in sort_fields]
        next_cursor = base64.b64encode(orjson.dumps(next_vals)).decode()

    return fast_json({"items": characters, "next_cursor": next_cursor})


@twa_auth("POST")
async def character_like_view(request, pk):
    try:
        payload = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        return R400

    wanted_active = payload.get("active")
    if wanted_active is None:
        return R400

    user_id = request.user.telegram_id

    def toggle_like_sync():
        if wanted_active:
            _, created = CharacterLike.objects.get_or_create(
                user_id=user_id, character_id=pk
            )
            if created:
                Character.objects.filter(pk=pk).update(likes_count=F("likes_count") + 1)
        else:
            deleted_count, _ = CharacterLike.objects.filter(
                user_id=user_id, character_id=pk
            ).delete()
            if deleted_count > 0:
                Character.objects.filter(pk=pk, likes_count__gt=0).update(
                    likes_count=F("likes_count") - 1
                )

    await sync_to_async(toggle_like_sync)()
    return R204
