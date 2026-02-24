from django.urls import path

from .views import tariff_list_view

urlpatterns = [
    path("", tariff_list_view),
]
