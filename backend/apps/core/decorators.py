import logging
from functools import wraps

import jwt
from config.utils import R401, R405
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def jwt_auth(methods=None):
    if methods is None:
        methods = ["GET"]

    def decorator(view_func):
        @csrf_exempt
        @wraps(view_func)
        async def _wrapped(request, *args, **kwargs):
            if request.method not in methods:
                return R405

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return R401

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                if payload.get("type") != "access":
                    return R401

                request.user_id = payload["user_id"]
                return await view_func(request, *args, **kwargs)

            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return R401
            except Exception as e:
                logger.error(
                    f"JWT Auth Error in {view_func.__name__}: {str(e)}", exc_info=True
                )
                return R401

        return _wrapped

    return decorator
