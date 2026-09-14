from django.urls import include, path

from .auth import refresh_token_view, telegram_auth_view
from .character import (
    character_detail_view,
    character_list_view,
    create_character_view,
    toggle_favorite_view,
)
from .chat import chat_list_view, chat_messages_view, message_send_view
from .payment import create_payment_view, tariff_list_view, yookassa_webhook_view
from .user import (
    current_user_view,
    claim_daily_bonus_view,
    redeem_promocode_view,
    settings_info_view,
    update_llm_view,
    update_profile_view,
    user_profile_view,
)

auth_patterns = [
    path("telegram/", telegram_auth_view),
    path("refresh/", refresh_token_view),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/me/", current_user_view),
    path("users/daily-bonus/claim/", claim_daily_bonus_view),
    path("users/<int:user_id>/profile/", user_profile_view),
    path("users/settings/info/", settings_info_view),
    path("users/settings/update-llm/", update_llm_view),
    path("users/promocodes/redeem/", redeem_promocode_view),
    path("users/settings/update-profile/", update_profile_view),
    path("characters/", character_list_view),
    path("characters/create/", create_character_view),
    path("characters/<int:character_id>/", character_detail_view),
    path("characters/<int:character_id>/favorite/", toggle_favorite_view),
    path("chats/", chat_list_view),
    path("chats/<uuid:chat_id>/messages/", chat_messages_view),
    path("chats/character/<int:character_id>/send/", message_send_view),
    path("tariffs/", tariff_list_view),
    path("payments/create/", create_payment_view),
    path("webhooks/yookassa/", yookassa_webhook_view),
]
