import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if os.environ.get("CELERY_POOL_CLASS") == "gevent":
    from gevent import monkey

    monkey.patch_all()

    try:
        from psycogreen.gevent import patch_psycopg

        patch_psycopg()
    except ImportError:
        pass

app = Celery("aichat")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
