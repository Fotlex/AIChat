from django.urls import path

from .views import current_user_view, get_ws_token_view

urlpatterns = [
    path("me/", current_user_view),
    path("ws-token/", get_ws_token_view),
]
