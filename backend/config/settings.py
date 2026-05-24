from pathlib import Path

from .schema import conf

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = conf.DJANGO_SECRET_KEY
DEBUG = conf.DEBUG

ALLOWED_HOSTS = conf.ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = conf.CSRF_TRUSTED_ORIGINS

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "config.admin.CustomAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": conf.POSTGRES_DB,
        "USER": conf.POSTGRES_USER,
        "PASSWORD": conf.POSTGRES_PASSWORD,
        "HOST": conf.POSTGRES_HOST,
        "PORT": conf.POSTGRES_PORT,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "connect_timeout": 5,
            "pool": {
                "min_size": 2,
                "max_size": 15,
                "timeout": 10,
            },
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru"
TIME_ZONE = conf.TIMEZONE
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static_root"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

YOOKASSA_SHOP_ID = conf.YOOKASSA_SHOP_ID
YOOKASSA_SECRET_KEY = conf.YOOKASSA_SECRET_KEY

APP_URL = conf.APP_URL

ADMIN_SITE_HEADER = conf.ADMIN_SITE_HEADER
ADMIN_SITE_TITLE = conf.ADMIN_SITE_TITLE
ADMIN_INDEX_TITLE = conf.ADMIN_INDEX_TITLE
ADMIN_REORDER = [
    {"label": "👥 Пользователи", "models": ["core.User"]},
    {"label": "🎭 Персонажи", "models": ["core.Character"]},
    {"label": "💬 Чаты и Сообщения", "models": ["core.Conversation", "core.Message"]},
    {"label": "⚙️ Настройки LLM", "models": ["core.LLMConfiguration"]},
    {"label": "💳 Платежи и Промокоды", "models": [
        "core.Tariff", 
        "core.Transaction", 
        "core.Promocode"
    ]},
]
