from django.urls import include, path

from .auth import login_view, refresh_token_view, register_view
from .character import character_list_view
from .chat import chat_list_view, chat_messages_view, message_send_view
from .user import current_user_view, settings_info_view, update_llm_view, redeem_promocode_view, update_profile_view
from .payment import tariff_list_view, create_payment_view, yookassa_webhook_view

auth_patterns = [
    path("register/", register_view),
    path("login/", login_view),
    path("refresh/", refresh_token_view),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/me/", current_user_view),
    path("users/settings/info/", settings_info_view),
    path("users/settings/update-llm/", update_llm_view),
    path("users/promocodes/redeem/", redeem_promocode_view),
    path("users/settings/update-profile/", update_profile_view),
    path("characters/", character_list_view),
    path("chats/", chat_list_view),
    path("chats/<uuid:chat_id>/messages/", chat_messages_view),
    path("chats/character/<int:character_id>/send/", message_send_view),
    path("tariffs/", tariff_list_view),
    path("payments/create/", create_payment_view),
    path("webhooks/yookassa/", yookassa_webhook_view),
]
