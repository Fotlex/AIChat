from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/characters/", include("apps.characters.urls")),
    path("api/v1/chats/", include("apps.billing.urls")),
    path("api/v1/", include("apps.chat.urls")),
    path("api/v1/bot/", include("apps.bot.urls")),
]
