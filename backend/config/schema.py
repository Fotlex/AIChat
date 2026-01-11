from pydantic import RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DJANGO_SECRET_KEY: str
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str]
    CSRF_TRUSTED_ORIGINS: list[str]
    TIMEZONE: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB_CELERY_BROKER: int
    REDIS_DB_CELERY_RESULTS: int
    REDIS_DB_CACHE: int
    REDIS_DB_FSM: int

    WEBAPP_URL: str
    BOT_TOKEN: str
    BOT_WEBHOOK_SECRET: str

    CENTRIFUGO_API_URL: str
    CENTRIFUGO_API_KEY: str
    CENTRIFUGO_HMAC_SECRET: str

    ADMIN_SITE_HEADER: str
    ADMIN_SITE_TITLE: str
    ADMIN_INDEX_TITLE: str

    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=f"{self.REDIS_DB_CELERY_BROKER}",
            )
        )

    @computed_field
    @property
    def CELERY_RESULT_BACKEND_URL(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=f"{self.REDIS_DB_CELERY_RESULTS}",
            )
        )

    @computed_field
    @property
    def CACHE_URL(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=f"{self.REDIS_DB_CACHE}",
            )
        )

    @computed_field
    @property
    def FSM_URL(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=f"{self.REDIS_DB_FSM}",
            )
        )

    model_config = SettingsConfigDict(extra="ignore")


conf = Settings()
