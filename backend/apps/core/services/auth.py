from datetime import datetime, timedelta, timezone

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password


@sync_to_async
def hash_password_async(raw_password: str) -> str:
    return make_password(raw_password)


@sync_to_async
def verify_password_async(raw_password: str, encoded_password: str) -> bool:
    return check_password(raw_password, encoded_password)


def generate_tokens(user_id: int) -> dict:
    now = datetime.now(timezone.utc)
    access_exp = now + timedelta(minutes=60)
    refresh_exp = now + timedelta(days=7)

    access_token = jwt.encode(
        {"user_id": user_id, "exp": access_exp, "type": "access"},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    refresh_token = jwt.encode(
        {"user_id": user_id, "exp": refresh_exp, "type": "refresh"},
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return {"access": access_token, "refresh": refresh_token}
