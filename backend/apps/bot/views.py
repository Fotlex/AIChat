import logging
from http import HTTPStatus

import orjson
from aiogram.types import Update
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .authentication import validate_telegram_token
from .loader import bot, dp

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
async def bot_webhook(request: HttpRequest) -> HttpResponse:
    if not validate_telegram_token(request):
        return HttpResponseForbidden("Unauthorized")

    try:
        payload = orjson.loads(request.body)
        update = Update(**payload)

        await dp.feed_update(bot, update)

        return HttpResponse(status=HTTPStatus.OK)

    except orjson.JSONDecodeError:
        logger.warning("Webhook received invalid JSON payload")
        return HttpResponseBadRequest("Invalid JSON")

    except Exception:
        logger.exception("Critical error in webhook handler")
        return HttpResponse(status=HTTPStatus.OK)
