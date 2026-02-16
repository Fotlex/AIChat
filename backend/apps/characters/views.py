import base64

import orjson
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Character


class CharacterListView(APIView):
    permission_classes = [IsAuthenticated]

    SORT_CONFIG = {
        "recent": ("id",),
        "popular": ("likes_count", "id"),
    }

    def get(self, request):
        params = request.query_params
        limit = 40

        queryset = Character.objects.filter(is_active=True)

        is_yours = params.get("yours")
        if is_yours == "1":
            queryset = queryset.filter(creator_id=request.user.telegram_id)
        elif is_yours == "0":
            queryset = queryset.exclude(creator_id=request.user.telegram_id)

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

        order_by = [f"-{f}" for f in sort_fields]

        characters = list(
            queryset.order_by(*order_by)[: limit + 1].values(
                "id",
                "name",
                "gender",
                "description",
                "photo",
                "likes_count",
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
