from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.chat.services import centrifugo_service

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["get"], url_path="me")
    def current_user(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="ws-token")
    def get_ws_token(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)

        token = centrifugo_service.get_connection_token(request.user.telegram_id)
        return Response({"token": token})
