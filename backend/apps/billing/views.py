from asgiref.sync import sync_to_async
from config.utils import fast_json

from apps.users.auth import twa_auth

from .models import Tariff


@twa_auth("GET")
async def tariff_list_view(request):
    tariffs = await sync_to_async(list)(
        Tariff.objects.values("id", "name", "cost", "reward", "photo")
    )
    return fast_json(tariffs)
