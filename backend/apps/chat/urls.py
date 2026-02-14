from django.urls import path

from .views import ChatDetailView, ChatListView, MessageSendView

urlpatterns = [
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path(
        "chats/character/<int:character_id>/",
        ChatDetailView.as_view(),
        name="chat-detail",
    ),
    path("chats/<int:chat_id>/send/", MessageSendView.as_view(), name="message-send"),
]
