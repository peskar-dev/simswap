import logging
import os
import shutil

from celery import states

from faceswap.celery import app
from faceswap.settings import ENVIRONMENT
from mainapp.models import VideoGenerationCount

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


@app.task(bind=True)
def generate_faceswap(self, file_path: str, video_path: str):
    """
    Generate a faceswap from a photo and a video.
    Then delete
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    logger.info(f"Processing file: {file_path}")
    self.update_state(state="in_progress")

    dir_name = os.path.dirname(file_path)

    output_path = os.path.join(dir_name, "output.mp4")
    try:
        roop.run(file_path, video_path, output_path)
    except Exception:
        logger.exception(f"Error processing file: {file_path}")
        raise
    finally:
        delete_dir.apply_async(args=[dir_name], countdown=60)
        self.update_state(
            state=states.SUCCESS,
            meta={"file_path": output_path},
        )
        VideoGenerationCount.increment_count()
