from rest_framework import viewsets

from .models import Character
from .serializers import CharacterListSerializer


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterListSerializer

    def get_queryset(self):
        return Character.objects.filter(is_active=True)
    
