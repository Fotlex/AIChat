from config.utils import fast_json

from apps.chat.services import centrifugo_service
from apps.users.auth import twa_auth


@twa_auth("GET")
async def current_user_view(request):
    user = request.user
    return fast_json(
        {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance": user.balance,
        }
    )


@twa_auth("GET")
async def get_ws_token_view(request):
    token = centrifugo_service.get_connection_token(request.user.telegram_id)
    return fast_json({"token": token})
