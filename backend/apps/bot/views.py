import logging

import orjson
from aiogram.types import Update
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .loader import bot, dp

logger = logging.getLogger(__name__)


async def set_webhook(request):
    if not request.user.is_superuser:
        return HttpResponse("Forbidden", status=403)

    webhook_url = f"{settings.WEBAPP_URL}/api/v1/bot/webhook/"

    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.BOT_WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=[
                "message",
                "callback_query",
                "pre_checkout_query",
            ],
        )
        return HttpResponse(f"Webhook set successfully to: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return HttpResponse(f"Error: {e}", status=500)


@csrf_exempt
async def bot_webhook(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.BOT_WEBHOOK_SECRET:
        logger.warning(
            f"SECURITY: Invalid webhook secret from IP {request.META.get('REMOTE_ADDR')}"
        )
        return HttpResponse("Unauthorized", status=403)

    try:
        payload = orjson.loads(request.body)

        update = Update(**payload)

        await dp.feed_update(bot, update)

        return JsonResponse({"status": "ok"})

    except orjson.JSONDecodeError:
        logger.warning("Webhook received invalid JSON")
        return HttpResponse("Invalid JSON", status=400)

    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        return HttpResponse("Error handled", status=200)
