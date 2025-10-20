import logging
from typing import Optional, Tuple

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError

from .models import User

logger = logging.getLogger(__name__)


class TWAAuthentication(BaseAuthentication):
    def __init__(self):
        self.authenticator = TelegramAuthenticator(settings.TELEGRAM_SECRET_KEY)

    def authenticate(self, request: Request) -> Optional[Tuple[User, None]]:
        auth_header = request.headers.get("Telegram-Init-Data")

        if not auth_header:
            logger.warning("TWA Auth header is missing for request")
            raise AuthenticationFailed("Telegram-Init-Data header is missing.")

        try:
            init_data = self.authenticator.validate(auth_header)
        except InvalidInitDataError as e:
            logger.warning(f"Invalid Telegram InitData received: {e}")
            raise AuthenticationFailed("Invalid Telegram authentication data")

        user, created = User.objects.get_or_create(
            telegram_id=init_data.user.id,
            defaults={
                "username": init_data.user.username,
                "first_name": init_data.user.first_name,
                "last_name": init_data.user.last_name,
            },
        )

        if created:
            logger.info(f"New user created: {user}")
            self._handle_referral(user, init_data.start_param)

        return user, None

    def _handle_referral(self, user: User, start_param: Optional[str]) -> None:
        if not start_param or not start_param.isdigit():
            return

        referrer_id = int(start_param)
        if user.telegram_id == referrer_id:
            return

        referrer = User.objects.filter(telegram_id=referrer_id).first()

        if referrer:
            user.referrer = referrer
            user.save(update_fields=["referrer"])
            logger.info(f"User {user} was referred by {referrer}")

    def authenticate_header(self, request: Request) -> str:
        return "TWA"
