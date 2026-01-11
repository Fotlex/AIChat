import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(self):
        self.api_key = settings.AI_PROVIDER_KEY
        self.api_url = settings.AI_PROVIDER_URL
        self.timeout = httpx.Timeout(60.0, connect=5.0)

    async def generate_response(
        self, messages: list[dict], model: str = "openai/gpt-3.5-turbo"
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.SITE_URL,
            "X-Title": "AIChat",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.api_url, json=payload, headers=headers
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                logger.error(f"AI Provider Error: {str(e)}")
                raise e
