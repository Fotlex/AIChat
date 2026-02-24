from django.urls import path

from .views import character_like_view, character_list_view

urlpatterns = [
    path("", character_list_view),
    path("<int:pk>/like/", character_like_view),
]
