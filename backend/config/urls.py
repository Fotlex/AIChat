from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .utils import scoped_middleware

urlpatterns = [
    path(
        "admin/", include(scoped_middleware(settings.ADMIN_MIDDLEWARE, admin.site.urls))
    ),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/characters/", include("apps.characters.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/chats/", include("apps.chat.urls")),
    path("api/v1/bot/", include("apps.bot.urls")),
]
