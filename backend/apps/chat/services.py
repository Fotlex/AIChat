import logging
import time

import httpx
import jwt
from django.conf import settings

logger = logging.getLogger(__name__)


class CentrifugoService:
    def __init__(self):
        self._api_url = settings.CENTRIFUGO_API_URL
        self._headers = {
            "Content-Type": "application/json",
            "X-API-Key": settings.CENTRIFUGO_API_KEY,
        }
        self._client = httpx.Client(
            headers=self._headers,
            timeout=httpx.Timeout(5.0, connect=2.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    def get_connection_token(self, user_id: int) -> str:
        claims = {
            "sub": str(user_id),
            "exp": int(time.time()) + 24 * 3600,
        }
        return jwt.encode(claims, settings.CENTRIFUGO_HMAC_SECRET, algorithm="HS256")

    def publish_personal_message(self, user_id: int, event_type: str, payload: dict):
        channel = f"personal:#{user_id}"

        data = {
            "method": "publish",
            "params": {
                "channel": channel,
                "data": {"type": event_type, "payload": payload},
            },
        }

        try:
            response = self._client.post(self._api_url, json=data)

            if response.status_code != 200:
                logger.error(
                    f"Centrifugo API error: status={response.status_code} "
                    f"body={response.text[:200]}"
                )
                return

            result = response.json()
            if result.get("error"):
                logger.error(f"Centrifugo business error: {result['error']}")
            else:
                logger.debug(f"Centrifugo: successful publish to {channel}")

        except httpx.HTTPError as e:
            logger.error(f"Centrifugo connection failed: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error in CentrifugoService: {str(e)}")


centrifugo_service = CentrifugoService()
