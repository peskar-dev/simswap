import glob
import mimetypes
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

import onnxruntime
import tensorflow
from roop.rooplib import config
from tqdm import tqdm

TEMP_DIRECTORY = "temp"
TEMP_VIDEO_FILE = "temp.mp4"


# # monkey patch ssl for mac
# if platform.system().lower() == 'darwin':
#     ssl._create_default_https_context = ssl._create_unverified_context


def run_ffmpeg(args: list[str]) -> bool:
    commands = ["ffmpeg", "-hide_banner", "-loglevel", config.log_level]
    commands.extend(args)
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except Exception:
        pass
    return False


def extract_frames(target_path: str, fps: float = config.fps) -> bool:
    temp_directory_path = get_temp_directory_path(target_path)
    temp_frame_quality = config.temp_frame_quality * 31 // 100
    return run_ffmpeg(
        [
            "-hwaccel",
            "auto",
            "-i",
            target_path,
            "-q:v",
            str(temp_frame_quality),
            "-pix_fmt",
            "rgb24",
            "-vf",
            "fps=" + str(fps),
            os.path.join(
                temp_directory_path, "%04d." + config.temp_frame_format
            ),
        ]
    )


def create_video(frame_dir: str, fps: float = 30) -> bool:
    temp_output_path = get_temp_output_path(frame_dir)
    output_video_quality = (config.output_video_quality + 1) * 51 // 100
    commands = [
        "-hwaccel",
        "auto",
        "-r",
        str(fps),
        "-i",
        os.path.join(frame_dir, "%04d." + config.temp_frame_format),
        "-c:v",
        config.output_video_encoder,
    ]
    if config.output_video_encoder in ["libx264", "libx265", "libvpx"]:
        commands.extend(["-crf", str(output_video_quality)])
    if config.output_video_encoder in ["h264_nvenc", "hevc_nvenc"]:
        commands.extend(["-cq", str(output_video_quality)])
    commands.extend(
        [
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "colorspace=bt709:iall=bt601-6-625:fast=1",
            "-y",
            temp_output_path,
        ]
    )
    return run_ffmpeg(commands)


def restore_audio(target_path: str, frame_dir: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(frame_dir)
    commands = [
        "-hwaccel",
        "auto",
        "-i",
        temp_output_path,
        "-i",
        target_path,
        "-c:v",
        "copy",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-y",
        output_path,
    ]
    done = run_ffmpeg(commands)
    if not done:
        move_temp(target_path, output_path)


def get_temp_frame_paths(target_path: str) -> list[str]:
    return glob.glob(
        (
            os.path.join(
                glob.escape(target_path), "*." + config.temp_frame_format
            )
        )
    )


def get_temp_directory_path(target_path: str) -> str:
    return os.path.join(config.temp_directory, TEMP_DIRECTORY)


def get_temp_output_path(target_path: str) -> str:
    return os.path.join(target_path, TEMP_VIDEO_FILE)


def create_temp(target_path: str) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    shutil.rmtree(temp_directory_path, ignore_errors=True)
    Path(temp_directory_path).mkdir(parents=True)


def move_temp(target_path: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(target_path)
    if os.path.isfile(temp_output_path):
        if os.path.isfile(output_path):
            os.remove(output_path)
        shutil.move(temp_output_path, output_path)


def is_image(image_path: str) -> bool:
    if image_path and os.path.isfile(image_path):
        mimetype, _ = mimetypes.guess_type(image_path)
        return bool(mimetype and mimetype.startswith("image/"))
    return False


def is_video(video_path: str) -> bool:
    if video_path and os.path.isfile(video_path):
        mimetype, _ = mimetypes.guess_type(video_path)
        return bool(mimetype and mimetype.startswith("video/"))
    return False


def conditional_download(
    download_directory_path: str, urls: list[str]
) -> None:
    if not os.path.exists(download_directory_path):
        os.makedirs(download_directory_path)
    for url in urls:
        download_file_path = os.path.join(
            download_directory_path, os.path.basename(url)
        )
        if not os.path.exists(download_file_path):
            request = urllib.request.urlopen(url)  # type: ignore[attr-defined]
            total = int(request.headers.get("Content-Length", 0))
            with tqdm(
                total=total,
                desc="Downloading",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress:
                urllib.request.urlretrieve(
                    url,
                    download_file_path,
                    reporthook=lambda count, block_size, total_size: progress.update(
                        block_size
                    ),
                )  # type: ignore[attr-defined]


def resolve_relative_path(path: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def limit_resources() -> None:
    # prevent tensorflow memory leak
    gpus = tensorflow.config.experimental.list_physical_devices("GPU")
    for gpu in gpus:
        tensorflow.config.experimental.set_virtual_device_configuration(
            gpu,
            [
                tensorflow.config.experimental.VirtualDeviceConfiguration(
                    memory_limit=1024
                )
            ],
        )


def decode_execution_providers(execution_providers: list[str]) -> list[str]:
    return [
        provider
        for provider, encoded_execution_provider in zip(
            onnxruntime.get_available_providers(),
            encode_execution_providers(onnxruntime.get_available_providers()),
        )
        if any(
            execution_provider in encoded_execution_provider
            for execution_provider in execution_providers
        )
    ]


def encode_execution_providers(execution_providers: list[str]) -> list[str]:
    return [
        execution_provider.replace("ExecutionProvider", "").lower()
        for execution_provider in execution_providers
    ]
