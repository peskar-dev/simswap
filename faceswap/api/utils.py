import json
import logging
import os
import tempfile
from typing import TypedDict

from billiard.exceptions import SoftTimeLimitExceeded
from celery.result import AsyncResult
from django.core.exceptions import SuspiciousFileOperation
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from faceswap.celery import app as celery_app
from faceswap.settings import BASE_DIR, redis_client
from kombu.exceptions import OperationalError
from mainapp.models import Video
from rest_framework import exceptions

from .tasks import generate_faceswap

logger = logging.getLogger(__name__)


class TaskStatusDict(TypedDict):
    queue: int | None
    status: str
    file_path: str | None


def get_task_position(task_id: str) -> TaskStatusDict | None:
    task = AsyncResult(task_id, app=celery_app)
    task_status = str(task.status).lower()

    if task_status in ("in_progress", "success"):
        file_path = (
            task.result.get("file_path")
            if task.result and task_status == "success"
            else None
        )
        if file_path and not os.path.exists(file_path):
            return None
        return {"queue": None, "status": task_status, "file_path": file_path}

    for index, task_payload in enumerate(
        reversed(redis_client.lrange("celery", 0, -1))
    ):
        if json.loads(task_payload)["headers"]["id"] == task.id:
            return {
                "queue": index + 1,
                "status": "pending",
                "file_path": None,
            }
    return None


def save_file(file: File) -> str:
    try:
        output_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(dir=output_dir)
        os.chmod(temp_dir, 0o755)

        fs = FileSystemStorage(location=temp_dir)
        file_name = fs.save(file.name, file)

        return fs.path(file_name)
    except SuspiciousFileOperation:
        logger.exception("Suspicious file operation")
        raise exceptions.ValidationError("Suspicious file operation")


def create_task(file_path: str) -> AsyncResult:
    video_instance = Video.objects.filter(show=True).first()
    video_path = video_instance.video_file.url
    try:
        return generate_faceswap.delay(file_path, video_path)
    except (SoftTimeLimitExceeded, OperationalError):
        logger.exception("Internal server error")
        raise exceptions.APIException("Internal server error")
