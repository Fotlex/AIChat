from rest_framework import viewsets

from .models import Tariff
from .serializers import TariffListSerializer


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TariffListSerializer

    def get_queryset(self):
        return Tariff.objects.all()