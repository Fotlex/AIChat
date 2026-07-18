import logging
import secrets

import orjson
from aiogram.types import Update
from config.utils import R200, R403, R405
from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from .engine import bot, get_configured_dispatcher

logger = logging.getLogger(__name__)


def validate_telegram_token(request: HttpRequest) -> bool:
    secret = getattr(settings, "TELEGRAM_BOT_WEBHOOK_SECRET", None)
    if not secret:
        return True

    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not token:
        return False

    if not secrets.compare_digest(token, secret):
        return False

    return True


@csrf_exempt
async def telegram_webhook_view(request: HttpRequest):
    if request.method != "POST":
        return R405

    if not validate_telegram_token(request):
        return R403

    try:
        payload = orjson.loads(request.body)
        update = Update(**payload)

        dp = get_configured_dispatcher()
        await dp.feed_update(bot, update)

        return R200
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}", exc_info=True)
        return R200
