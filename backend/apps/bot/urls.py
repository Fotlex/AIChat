from django.urls import path

from .views import bot_webhook

urlpatterns = [
    path("webhook/", bot_webhook, name="bot-webhook"),
]
