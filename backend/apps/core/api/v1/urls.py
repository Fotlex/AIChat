from django.urls import include, path

from .auth import login_view, refresh_token_view, register_view
from .character import character_list_view
from .chat import chat_list_view, chat_messages_view, message_send_view
from .user import current_user_view

auth_patterns = [
    path("register/", register_view),
    path("login/", login_view),
    path("refresh/", refresh_token_view),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/me/", current_user_view),
    path("characters/", character_list_view),
    path("chats/", chat_list_view),
    path("chats/<uuid:chat_id>/messages/", chat_messages_view),
    path("chats/character/<int:character_id>/send/", message_send_view),
]
