import jwt
import orjson
from config.utils import R400, R401, R405, fast_json
from django.conf import settings
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import User
from apps.core.services.auth import generate_tokens, validate_telegram_init_data
from apps.core.services.referral import process_referral_async


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
            return fast_json({"error": "Invalid signature or expired data"}, status=401)

        tg_user_str = validated_data.get("user")
        if not tg_user_str:
            return R400

        tg_user = orjson.loads(tg_user_str)
        tg_id = tg_user.get("id")
        tg_username = tg_user.get("username")

        start_param = validated_data.get("start_param", "")
        referrer_id = None
        if start_param:
            try:
                clean_param = start_param.replace("ref_", "")
                referrer_id = int(clean_param)
            except ValueError:
                pass

        user = await User.objects.filter(id=tg_id).afirst()
        is_new_user = False

        if not user:
            base_username = tg_username if tg_username else f"user_{tg_id}"

            try:
                user = await User.objects.acreate(
                    id=tg_id, username=base_username[:64], balance=1000
                )
                is_new_user = True
            except IntegrityError:
                user = await User.objects.filter(id=tg_id).afirst()

        if is_new_user and referrer_id:
            await process_referral_async(referred_id=user.id, referrer_id=referrer_id)

        tokens = generate_tokens(user.id)
        return fast_json(tokens, status=200)

    except Exception:
        return fast_json({"error": "Internal auth error"}, status=400)


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
