from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("backend.users.urls")),
    path("api/v1/", include("backend.characters.urls")),
    path("api/v1/", include("backend.payments.urls")),
    path("api/v1/", include("backend.chats.urls")),
]
