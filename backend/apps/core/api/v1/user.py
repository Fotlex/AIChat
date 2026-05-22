from config.utils import fast_json

from apps.core.decorators import jwt_auth
from apps.core.models import User


@jwt_auth(methods=["GET"])
async def current_user_view(request):
    user = (
        await User.objects.filter(id=request.user_id)
        .values("id", "username", "balance")
        .afirst()
    )
    if not user:
        return fast_json({"error": "User not found"}, status=404)
    return fast_json(user)
