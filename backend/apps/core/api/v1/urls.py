from django.urls import include, path

from .auth import login_view, register_view
from .user import current_user_view

auth_patterns = [
    path("register/", register_view),
    path("login/", login_view),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/me/", current_user_view),
]
