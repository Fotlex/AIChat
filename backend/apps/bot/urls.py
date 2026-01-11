from django.urls import path

from .views import bot_webhook, set_webhook

urlpatterns = [
    path("webhook/", bot_webhook, name="bot_webhook"),
    path("set-webhook/", set_webhook, name="bot_set_webhook"),
]
