import os

from celery import Celery
from celery.signals import worker_before_create_process
from faceswap.settings import ENVIRONMENT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faceswap.settings")

app = Celery("faceswap")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.task_routes = {
    "api.tasks.delete_dir": {"queue": "delete"},
}

# if ENVIRONMENT == "production":
# from roop.rooplib.face_analyser import get_face_analyser
# from roop.rooplib.processors.frame.face_swapper import get_face_swapper
#
# @worker_before_create_process.connect
# def pre_fork(*_, **__):
#
#     get_face_analyser()
#     get_face_swapper()
