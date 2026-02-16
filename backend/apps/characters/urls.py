from django.urls import path

from .views import CharacterLikeView, CharacterListView

app_name = "characters"

urlpatterns = [
    path("", CharacterListView.as_view(), name="list"),
    path("<int:pk>/like/", CharacterLikeView.as_view(), name="like"),
]
