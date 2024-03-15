import logging
import os
import shutil
import signal
import time

from celery import states
from celery.exceptions import MaxRetriesExceededError
from faceswap.celery import app
from faceswap.settings import ENVIRONMENT
from mainapp.models import VideoGenerationCount
from onnxruntime.capi.onnxruntime_pybind11_state import Fail as OnnxFail
from onnxruntime.capi.onnxruntime_pybind11_state import (
    RuntimeException as OnnxRuntimeException,
)

if ENVIRONMENT == "production":
    import roop
else:
    from .roop_mock import Roop

    roop = Roop()

logger = logging.getLogger(__name__)


@app.task
def delete_dir(dir_name: str):
    """
    Delete a directory and its contents.
    """
    if not os.path.exists(dir_name):
        logger.error(f"Directory not found: {dir_name}")
        raise FileNotFoundError(f"Directory not found: {dir_name}")
    logger.info(f"Deleting directory: {dir_name}")
    try:
        shutil.rmtree(dir_name)
    except Exception:
        logger.exception(f"Error deleting directory: {dir_name}")
        raise


@app.task(bind=True, max_retries=3)
def generate_faceswap(self, file_path: str, video_path: str):
    """
    Generate a faceswap from a photo and a video.
    Then delete
    """

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.path.exists(video_path):
        logger.error(f"File not found: {video_path}")
        raise FileNotFoundError(f"File not found: {video_path}")
    logger.info(f"Processing file: {file_path}")
    self.update_state(state="in_progress")

    dir_name = os.path.dirname(file_path)

    output_path = os.path.join(dir_name, "output.mp4")
    try:
        roop.run(file_path, video_path, output_path)
    except (OnnxFail, OnnxRuntimeException) as exc:
        logger.error(f"OnnxFail processing file: {file_path}")
        raise self.retry(exc=exc, countdown=10)
    except Exception as exc:
        if str(exc) == "Face not found on source image":
            logger.warning(f"Face not found")
        else:
            logger.exception(f"Error processing file: {file_path}")
            raise self.retry(exc=exc)
    else:
        delete_dir.apply_async(args=[dir_name], countdown=600, queue="delete")
        self.update_state(
            state=states.SUCCESS,
            meta={"file_path": output_path},
        )
