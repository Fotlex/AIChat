import jwt
import orjson
from config.utils import R400, R401, R405, fast_json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import User
from apps.core.services.auth import generate_tokens, validate_telegram_init_data

@csrf_exempt
async def telegram_auth_view(request):
    if request.method != "POST":
        return R405

    try:
        data = orjson.loads(request.body)
        init_data = data.get("initData")

        if not init_data:
            return R400

        validated_data = validate_telegram_init_data(init_data)
        if not validated_data:
            return fast_json({"error": "Invalid signature"}, status=401)

        tg_user_str = validated_data.get('user')
        if not tg_user_str:
            return R400
            
        tg_user = orjson.loads(tg_user_str)
        tg_id = tg_user.get("id")
        tg_username = tg_user.get("username")

        user = await User.objects.filter(id=tg_id).afirst()
        if not user:
            base_username = tg_username if tg_username else f"user_{tg_id}"
            exists = await User.objects.filter(username=base_username).aexists()
            final_username = f"{base_username}_{tg_id}" if exists else base_username

            user = await User.objects.acreate(
                id=tg_id,
                username=final_username[:64],
                balance=1000
            )

        tokens = generate_tokens(user.id)
        return fast_json(tokens, status=200)

    except Exception as e:
        return fast_json({"error": str(e)}, status=400)


@csrf_exempt
async def refresh_token_view(request):
    if request.method != "POST":
        return R405
    try:
        data = orjson.loads(request.body)
        refresh_token = data.get("refresh")

        if not refresh_token:
            return R400

        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "refresh":
            return R401

        tokens = generate_tokens(payload["user_id"])
        return fast_json(tokens, status=200)

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return R401
    except orjson.JSONDecodeError:
        return R400