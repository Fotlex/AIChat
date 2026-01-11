import abc
import logging
import os

import requests

logger = logging.getLogger(__name__)


class BaseAIProvider(abc.ABC):
    @abc.abstractmethod
    def generate_response(self, messages: list[dict]) -> str:
        pass


class OpenRouterProvider(BaseAIProvider):
    def __init__(self, model: str):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = os.getenv("OPENROUTER_API_URL")
        self.model = model

        if not self.api_key or not self.api_url:
            raise ValueError(
                "OPENROUTER_API_KEY and OPENROUTER_API_URL must be set in .env"
            )

    def generate_response(self, messages: list[dict]) -> str:
        try:
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.85,
                    "max_tokens": 4000,
                },
                timeout=180,
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {e}")
            if response:
                logger.error(
                    f"Response status: {response.status_code}, body: {response.text}"
                )
            raise


def get_ai_provider(model_name: str) -> BaseAIProvider:
    return OpenRouterProvider(model=model_name)
