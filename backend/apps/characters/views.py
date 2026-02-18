import base64

import orjson
from django.db import transaction
from django.db.models import Exists, F, IntegerField, OuterRef, Q, Subquery
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.chat.models import Chat

from .models import Character, CharacterLike


class CharacterListView(APIView):
    permission_classes = [IsAuthenticated]

    SORT_CONFIG = {
        "recent": ("id",),
        "popular": ("likes_count", "id"),
    }

    def get(self, request):
        params = request.query_params
        limit = 30

        user = request.user
        queryset = Character.objects.filter(is_active=True)

        is_yours = params.get("yours")
        if is_yours == "1":
            queryset = queryset.filter(creator_id=user.telegram_id)
        elif is_yours == "0":
            queryset = queryset.exclude(creator_id=user.telegram_id)

        gender = params.get("gender")
        if gender in ("M", "F"):
            queryset = queryset.filter(gender=gender)

        sort_key = params.get("sort", "recent")
        sort_fields = self.SORT_CONFIG.get(sort_key, self.SORT_CONFIG["recent"])

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
            except Exception:
                pass

        chat_id_subquery = Chat.objects.filter(
            user=user, character=OuterRef("pk")
        ).values("id")[:1]

        is_liked_exists = CharacterLike.objects.filter(
            user=user, character=OuterRef("pk")
        )

        queryset = queryset.annotate(
            chat_id=Subquery(chat_id_subquery, output_field=IntegerField()),
            is_liked=Exists(is_liked_exists)
        )

        order_by = [f"-{f}" for f in sort_fields]

        characters = list(
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
        )

        has_more = len(characters) > limit
        next_cursor = None

        if has_more:
            characters.pop()
            last_item = characters[-1]
            next_vals = [last_item[f] for f in sort_fields]
            next_cursor = base64.b64encode(orjson.dumps(next_vals)).decode()

        for char in characters:
            if char["photo"]:
                char["photo"] = f"/media/{char['photo']}"

        return HttpResponse(
            orjson.dumps(
                {
                    "items": characters,
                    "next_cursor": next_cursor,
                }
            ),
            content_type="application/json",
        )


class CharacterLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        wanted_active = request.data.get("active")

        if wanted_active is None:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if wanted_active:
                _, created = CharacterLike.objects.get_or_create(
                    user=user, character_id=pk
                )

                if created:
                    Character.objects.filter(pk=pk).update(
                        likes_count=F("likes_count") + 1
                    )

            else:
                deleted_count, _ = CharacterLike.objects.filter(
                    user=user, character_id=pk
                ).delete()

                if deleted_count > 0:
                    Character.objects.filter(pk=pk, likes_count__gt=0).update(
                        likes_count=F("likes_count") - 1
                    )

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
