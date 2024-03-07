import logging
import time

logger = logging.getLogger(__name__)


class Roop:
    @staticmethod
    def run(file_path: str, video_path: str, output_path: str):
        time.sleep(20)
        logger.debug(
            f"Running Roop.run with file_path={file_path}, "
            f"video_path={video_path}, "
            f"output_path={output_path}"
        )
        with open(output_path, "w") as f:
            f.write("Это пример текста.")

    @staticmethod
    def prepare(target_path: str):
        logger.debug(f"Running Roop.prepare with target_path={target_path}")
