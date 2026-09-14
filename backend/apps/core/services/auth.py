import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

import jwt
from django.conf import settings

TELEGRAM_STATIC_SECRET = hmac.new(
    b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256
).digest()


def validate_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed_data = dict(parse_qsl(init_data))
        if "hash" not in parsed_data:
            return None

        auth_date = int(parsed_data.get("auth_date", 0))
        current_time = int(time.time())

        if abs(current_time - auth_date) > 86400:
            return None

        hash_value = parsed_data.pop("hash")
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )

        calculated_hash = hmac.new(
            TELEGRAM_STATIC_SECRET, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if calculated_hash == hash_value:
            return parsed_data
        return None
    except Exception:
        return None


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
