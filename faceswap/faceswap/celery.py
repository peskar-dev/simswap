import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faceswap.settings")

app = Celery("faceswap")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
