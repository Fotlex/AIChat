from rest_framework.generics import ListAPIView
from .models import Character
from .serializers import CharacterListSerializer

class CharacterListView(ListAPIView):
    serializer_class = CharacterListSerializer

    def get_queryset(self):
        return Character.objects.filter(is_active=True)