import orjson
from config.utils import R400, R405, fast_json
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import User
from apps.core.services.auth import (
    generate_tokens,
    hash_password_async,
    verify_password_async,
)


@csrf_exempt
async def register_view(request):
    if request.method != "POST":
        return R405

    try:
        data = orjson.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return fast_json({"error": "Username and password required"}, status=400)

        hashed_pw = await hash_password_async(password)

        user = await User.objects.acreate(
            username=username, password_hash=hashed_pw, balance=1000
        )

        tokens = generate_tokens(user.id)
        return fast_json(tokens, status=201)

    except IntegrityError:
        return fast_json({"error": "User exist"}, status=409)
    except orjson.JSONDecodeError:
        return R400


@csrf_exempt
async def login_view(request):
    if request.method != "POST":
        return R405

    try:
        data = orjson.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return R400

        user_data = (
            await User.objects.filter(username=username)
            .values("id", "password_hash")
            .afirst()
        )

        if not user_data:
            return fast_json({"error": "Invalid credentials"}, status=401)

        is_valid = await verify_password_async(password, user_data["password_hash"])
        if not is_valid:
            return fast_json({"error": "Invalid credentials"}, status=401)

        tokens = generate_tokens(user_data["id"])
        return fast_json(tokens, status=200)

    except orjson.JSONDecodeError:
        return R400
