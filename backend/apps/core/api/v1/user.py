import orjson
from config.utils import R400, R404, fast_json
from django.db.models import F
from django.utils import timezone

from apps.core.decorators import jwt_auth
from apps.core.models import (
    Character,
    LLMConfiguration,
    Promocode,
    PromocodeUsage,
    Referral,
    User,
)


@jwt_auth(methods=["GET"])
async def current_user_view(request):
    user = (
        await User.objects.filter(id=request.user_id)
        .values("id", "username", "balance")
        .afirst()
    )
    if not user:
        return fast_json({"error": "User not found"}, status=404)
    return fast_json(user)


@jwt_auth(methods=["GET"])
async def settings_info_view(request):
    user_data = (
        await User.objects.filter(id=request.user_id)
        .values("username", "balance", "preferred_llm_id")
        .afirst()
    )

    referrals_count = await Referral.objects.filter(
        referrer_id=request.user_id
    ).acount()
    user_data["referrals_count"] = referrals_count

    my_characters = [
        {
            "id": c["id"],
            "name": c["name"],
            "photo": f"/media/{c['avatar']}" if c["avatar"] else None,
            "likes": c["interaction_count"],
        }
        async for c in Character.objects.filter(author_id=request.user_id)
        .values("id", "name", "avatar", "interaction_count")
        .order_by("-created_at")
    ]

    llms = [
        llm
        async for llm in LLMConfiguration.objects.filter(is_active=True).values(
            "id", "name", "cost_per_request", "is_active"
        )
    ]

    return fast_json({"user": user_data, "llms": llms, "my_characters": my_characters})


@jwt_auth(methods=["GET"])
async def user_profile_view(request, user_id):
    if user_id == 0:
        user_data = {"id": 0, "username": "Система"}
        author_id_filter = None
    else:
        user_data = (
            await User.objects.filter(id=user_id).values("id", "username").afirst()
        )
        if not user_data:
            return R404
        author_id_filter = user_id

    author_characters = [
        {
            "id": c["id"],
            "name": c["name"],
            "photo": f"/media/{c['avatar']}" if c["avatar"] else None,
        }
        async for c in Character.objects.filter(
            author_id=author_id_filter, is_public=True
        ).values("id", "name", "avatar")
    ]

    return fast_json({"user": user_data, "characters": author_characters})


@jwt_auth(methods=["POST"])
async def update_profile_view(request):
    try:
        data = orjson.loads(request.body)
        new_username = data.get("username", "").strip()
    except Exception:
        return R400

    if not new_username or len(new_username) < 3:
        return fast_json({"error": "Ник слишком короткий"}, status=400)

    exists = (
        await User.objects.filter(username=new_username)
        .exclude(id=request.user_id)
        .aexists()
    )
    if exists:
        return fast_json({"error": "Этот ник уже занят"}, status=409)

    await User.objects.filter(id=request.user_id).aupdate(username=new_username)
    return fast_json({"status": "ok", "username": new_username})


@jwt_auth(methods=["POST"])
async def update_llm_view(request):
    try:
        data = orjson.loads(request.body)
        llm_id = data.get("llm_id")
    except Exception:
        return R400
    await User.objects.filter(id=request.user_id).aupdate(preferred_llm_id=llm_id)
    return fast_json({"status": "ok"})


@jwt_auth(methods=["POST"])
async def redeem_promocode_view(request):
    try:
        data = orjson.loads(request.body)
        code_text = data.get("code", "").strip()
    except Exception:
        return R400

    promo = await Promocode.objects.filter(
        code__iexact=code_text, is_active=True
    ).afirst()

    if not promo:
        return fast_json({"error": "Промокод не найден"}, status=404)

    if promo.expires_at and promo.expires_at < timezone.now():
        return fast_json({"error": "Срок действия истек"}, status=400)

    if promo.current_uses >= promo.max_uses:
        return fast_json({"error": "Промокод больше не действителен"}, status=400)

    already_used = await PromocodeUsage.objects.filter(
        user_id=request.user_id, promocode_id=promo.id
    ).aexists()

    if already_used:
        return fast_json({"error": "Вы уже использовали этот код"}, status=400)

    await User.objects.filter(id=request.user_id).aupdate(
        balance=F("balance") + promo.reward
    )
    await Promocode.objects.filter(id=promo.id).aupdate(
        current_uses=F("current_uses") + 1
    )
    await PromocodeUsage.objects.acreate(user_id=request.user_id, promocode_id=promo.id)

    return fast_json({"message": f"Начислено {promo.reward} монет!"})
