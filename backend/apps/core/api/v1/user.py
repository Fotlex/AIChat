import orjson
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from config.utils import fast_json, R400
from apps.core.decorators import jwt_auth
from apps.core.models import User, LLMConfiguration, Promocode, PromocodeUsage, Character


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
    user_obj = await User.objects.filter(id=request.user_id).afirst()
    
    my_characters = [
        {
            "id": c["id"],
            "name": c["name"],
            "photo": f"/media/{c['avatar']}" if c["avatar"] else None,
            "likes": c["interaction_count"]
        }
        async for c in Character.objects.filter(author_id=request.user_id).values(
            "id", "name", "avatar", "interaction_count"
        )
    ]
    
    llms = [
        {
            "id": l["id"],
            "name": l["name"],
            "cost": l["cost_per_request"],
            "is_active": l["is_active"]
        }
        async for l in LLMConfiguration.objects.filter(is_active=True).values()
    ]
    
    return fast_json({
        "user": {
            "username": user_obj.username,
            "balance": user_obj.balance,
            "preferred_llm_id": user_obj.preferred_llm_id
        },
        "llms": llms,
        "my_characters": my_characters
    })
    
    
@jwt_auth(methods=["POST"])
async def update_profile_view(request):
    try:
        data = orjson.loads(request.body)
        new_username = data.get("username", "").strip()
    except:
        return R400

    if not new_username or len(new_username) < 3:
        return fast_json({"error": "Ник слишком короткий"}, status=400)

    exists = await User.objects.filter(username=new_username).exclude(id=request.user_id).aexists()
    if exists:
        return fast_json({"error": "Этот ник уже занят"}, status=409)

    await User.objects.filter(id=request.user_id).aupdate(username=new_username)
    return fast_json({"status": "ok", "username": new_username})
    

@jwt_auth(methods=["POST"])
async def update_llm_view(request):
    try:
        data = orjson.loads(request.body)
        llm_id = data.get("llm_id")
    except:
        return R400
        
    await User.objects.filter(id=request.user_id).aupdate(preferred_llm_id=llm_id)
    return fast_json({"status": "ok"})

@jwt_auth(methods=["POST"])
async def redeem_promocode_view(request):
    try:
        data = orjson.loads(request.body)
        code_text = data.get("code", "").strip().upper()
    except:
        return R400

    promo = await Promocode.objects.filter(code=code_text, is_active=True).afirst()
    
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

    await User.objects.filter(id=request.user_id).aupdate(balance=F("balance") + promo.reward)
    await Promocode.objects.filter(id=promo.id).aupdate(current_uses=F("current_uses") + 1)
    await PromocodeUsage.objects.acreate(user_id=request.user_id, promocode_id=promo.id)

    return fast_json({
        "message": f"Начислено {promo.reward} монет!",
        "new_balance": "Обновится при следующем запросе"
    })