from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from .serializers import UserSerializer
from .models import User


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def current_user(self, request):
        user = request.tg_user
        serializer = UserSerializer(user)
        return Response(serializer.data)
