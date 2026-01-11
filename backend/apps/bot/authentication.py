import logging
import secrets

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def validate_telegram_token(request: HttpRequest) -> bool:
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if not token:
        logger.warning("Webhook Auth Failed: Missing header")
        return False

    if not secrets.compare_digest(token, settings.BOT_WEBHOOK_SECRET):
        logger.warning("Webhook Auth Failed: Invalid secret token")
        return False

    return True
