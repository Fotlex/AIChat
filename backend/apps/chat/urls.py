from django.urls import path

from .views import chat_detail_view, chat_list_view, message_send_view

urlpatterns = [
    path("", chat_list_view),
    path("<int:chat_id>/messages/", chat_detail_view),
    path("character/<int:character_id>/send/", message_send_view),
]
