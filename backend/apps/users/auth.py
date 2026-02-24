import logging
from functools import wraps

from asgiref.sync import sync_to_async
from config.utils import R401, R405, R500
from django.conf import settings
from telegram_webapp_auth import TelegramAuthenticator, generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from .services import get_or_create_user_with_referral

logger = logging.getLogger(__name__)

authenticator = TelegramAuthenticator(generate_secret_key(settings.BOT_TOKEN))


def twa_auth(method="GET"):
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped(request, *args, **kwargs):
            if request.method != method:
                return R405

            init_data_raw = request.headers.get("Telegram-Init-Data")
            if not init_data_raw:
                return R401

            try:
                init_data = authenticator.validate(init_data_raw)
            except InvalidInitDataError:
                return R401

            try:
                request.user = await sync_to_async(get_or_create_user_with_referral)(
                    init_data.user, init_data.start_param
                )

                return await view_func(request, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f"API Error in {view_func.__name__}: {str(e)}", exc_info=True
                )
                return R500

        return _wrapped

    return decorator
