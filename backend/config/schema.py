from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DJANGO_SECRET_KEY: str
    DEBUG: bool = False
    ALLOWED_HOSTS: str | list[str]
    CSRF_TRUSTED_ORIGINS: str | list[str]
    TIMEZONE: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str

    APP_URL: str
    TELEGRAM_BOT_TOKEN: str
    HF_TOKEN: str = ""

    ADMIN_SITE_HEADER: str = "AIChat Admin"
    ADMIN_SITE_TITLE: str = "Панель управления"
    ADMIN_INDEX_TITLE: str = "Добро пожаловать"

    @field_validator("ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS", mode="before")
    @classmethod
    def parse_env_list(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(extra="ignore")


conf = Settings()
