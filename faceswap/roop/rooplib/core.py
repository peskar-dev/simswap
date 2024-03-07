import shutil
import sys
import tempfile

from roop.rooplib import config
from roop.rooplib.config import frame_processors
from roop.rooplib.predictor import predict_video
from roop.rooplib.processors.frame.core import get_frame_processors_modules
from roop.rooplib.utilities import (
    create_temp,
    create_video,
    extract_frames,
    get_temp_directory_path,
    get_temp_frame_paths,
    is_video,
    limit_resources,
    restore_audio,
)


def update_status(message: str, scope: str = "ROOP.CORE") -> None:
    print(f"[{scope}] {message}")


def prepare_video(target_path: str) -> None:
    update_status("Running rooplib.core.prepare_video", "ROOP.CORE")
    if predict_video(target_path):
        destroy()
    update_status("Creating temporary resources...")
    create_temp(target_path)
    update_status(f"Extracting frames with {config.fps} FPS...")
    extract_frames(target_path)


def prepare(target_path: str) -> bool:
    update_status("Running rooplib.core.pre_check", "ROOP.CORE")
    if sys.version_info < (3, 9):
        update_status(
            "Python version is not supported - please upgrade to 3.9 or higher."
        )
        raise Exception(
            "Python version is not supported - please upgrade to 3.9 or higher."
        )
    if not shutil.which("ffmpeg"):
        update_status("ffmpeg is not installed.")
        raise Exception("ffmpeg is not installed.")

    limit_resources()

    for frame_processor in get_frame_processors_modules(frame_processors):
        try:
            frame_processor.pre_check()
        except:
            raise

    prepare_video(target_path)
    return True


def run(
    source_path: str,
    target_path: str,
    output_path: str,
) -> None:
    update_status("Running rooplib.core.run", "ROOP.CORE")

    gen_temp_path = tempfile.mkdtemp(dir=config.temp_directory)
    try:
        generate(source_path, target_path, output_path, gen_temp_path)
    except:
        update_status("An error occurred during processing...", "ROOP.CORE")
        raise
    finally:
        update_status(f"remove temp {gen_temp_path}", "ROOP.CORE")
        shutil.rmtree(gen_temp_path)


def generate(
    source_path: str,
    target_path: str,
    output_path: str,
    gen_temp_path: str,
) -> None:
    update_status("Running rooplib.core.generate", "ROOP.CORE")

    for frame_processor in get_frame_processors_modules(frame_processors):
        try:
            frame_processor.pre_start(source_path, target_path)
        except:
            raise

    temp_frame_path = get_temp_directory_path(target_path)
    update_status(f"Copy {temp_frame_path} to {gen_temp_path}", "ROOP.CORE")
    shutil.copytree(temp_frame_path, gen_temp_path, dirs_exist_ok=True)

    temp_frame_paths = get_temp_frame_paths(gen_temp_path)
    if temp_frame_paths:
        for frame_processor in get_frame_processors_modules(
            config.frame_processors
        ):
            update_status("Progressing...", frame_processor.NAME)
            frame_processor.process_video(source_path, temp_frame_paths)
            frame_processor.post_process()
    else:
        update_status("Frames not found...")
        raise Exception("Frames not found...")
        return

    update_status(f"Compile video from frames {gen_temp_path}", "ROOP.CORE")
    create_video(gen_temp_path)

    update_status(f"Restore audio from source {output_path}", "ROOP.CORE")
    restore_audio(target_path, gen_temp_path, output_path)

    if is_video(output_path):
        update_status(f"Processing to video succeed!: {output_path}")
    else:
        update_status("Processing to video failed!")
        raise Exception("Processing to video failed!")


def destroy() -> None:
    update_status("Running rooplib.core.destroy", "ROOP.CORE")
    sys.exit()
