from django.urls import path

from .views import ChatDetailView, ChatListView, MessageSendView

app_name = "chat"

urlpatterns = [
    path("", ChatListView.as_view(), name="list"),
    path("<int:chat_id>/messages/", ChatDetailView.as_view(), name="messages"),
    path("character/<int:character_id>/send/", MessageSendView.as_view(), name="send"),
]
