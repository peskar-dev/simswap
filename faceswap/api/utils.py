import logging
import os
import tempfile
from typing import TypedDict, Union

import orjson
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
        return handle_in_progress_or_success(task, task_status)

    if task_status == "pending":
        return handle_pending(task)

    return None


def handle_in_progress_or_success(
    task: AsyncResult, task_status: str
) -> TaskStatusDict | None:
    if task.ready() and task.result is not None:
        file_path = task.result.get("file_path")
        if not os.path.exists(file_path):
            return None
        file_path = str(os.path.relpath(str(file_path), f"{BASE_DIR}/outputs"))
    else:
        file_path = None
    return {"queue": None, "status": task_status, "file_path": file_path}


def handle_pending(task: AsyncResult) -> TaskStatusDict | None:
    reserved_tasks = get_reserved_tasks()
    if task.id in reserved_tasks:
        return {
            "queue": reserved_tasks[task.id] + 1,
            "status": "pending",
            "file_path": None,
        }

    queue: int = len(reserved_tasks)
    for raw_task_payload in reversed(redis_client.lrange("celery", 0, -1)):
        task_payload = orjson.loads(raw_task_payload)
        if task_payload["headers"]["task"] == "api.tasks.generate_faceswap":
            queue += 1
        if task_payload["headers"]["id"] == task.id:
            return {
                "queue": queue,
                "status": "pending",
                "file_path": None,
            }


def get_reserved_tasks() -> dict[str, int]:
    inspect = celery_app.control.inspect()
    reserved_dict: dict[str, int] = {}
    if not (reserved := inspect.reserved()):
        return reserved_dict
    for _, reserved_tasks in reserved.items():
        for reserved_task in reserved_tasks:
            if reserved_task["name"] == "api.tasks.generate_faceswap":
                reserved_dict[reserved_task["id"]] = reserved_tasks.index(
                    reserved_task
                )
    return reserved_dict


def save_file(file: File) -> str:
    try:
        output_dir = os.path.join(BASE_DIR, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(dir=output_dir)
        os.chmod(temp_dir, 0o755)

        fs = FileSystemStorage(location=temp_dir)
        file_name = fs.save(f"image.{file.name.split('.')[-1]}", file)

        return fs.path(file_name)
    except SuspiciousFileOperation:
        logger.exception("Suspicious file operation")
        raise exceptions.ValidationError("Suspicious file operation")


def create_task(file_path: str) -> AsyncResult:
    try:
        video_path = Video.related_video_path()
        return generate_faceswap.delay(file_path, video_path)
    except (SoftTimeLimitExceeded, OperationalError):
        logger.exception("Internal server error")
        raise exceptions.APIException("Internal server error")
