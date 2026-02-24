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
    "django_celery_beat",
    "apps.users",
    "apps.characters",
    "apps.chat",
    "apps.content",
    "apps.billing",
    "apps.bot",
]

MIDDLEWARE = []

ADMIN_MIDDLEWARE = [
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": conf.POSTGRES_DB,
        "USER": conf.POSTGRES_USER,
        "PASSWORD": conf.POSTGRES_PASSWORD,
        "HOST": "pgbouncer",
        "PORT": 6432,
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 5,
        },
        "DISABLE_SERVER_SIDE_CURSORS": True,
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

CELERY_BROKER_URL = conf.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = conf.CELERY_RESULT_BACKEND_URL
CELERY_TASK_IGNORE_RESULT = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": conf.CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

WEBAPP_URL = conf.WEBAPP_URL
BOT_TOKEN = conf.BOT_TOKEN
BOT_WEBHOOK_SECRET = conf.BOT_WEBHOOK_SECRET

FSM_URL = conf.FSM_URL

CENTRIFUGO_API_URL = conf.CENTRIFUGO_API_URL
CENTRIFUGO_API_KEY = conf.CENTRIFUGO_API_KEY
CENTRIFUGO_HMAC_SECRET = conf.CENTRIFUGO_HMAC_SECRET

ADMIN_SITE_HEADER = conf.ADMIN_SITE_HEADER
ADMIN_SITE_TITLE = conf.ADMIN_SITE_TITLE
ADMIN_INDEX_TITLE = conf.ADMIN_INDEX_TITLE
ADMIN_REORDER = [
    {"label": "👥 Пользователи", "models": ["users"]},
    {"label": "🎭 Персонажи", "models": ["characters"]},
    {"label": "💬 Чаты и Сообщения", "models": ["chat"]},
    {"label": "💎 Платежи и Тарифы", "models": ["billing"]},
    {"label": "⚙️ Контент бота", "models": ["content"]},
    {"label": "⏱️ Планировщик", "models": ["django_celery_beat"]},
]
