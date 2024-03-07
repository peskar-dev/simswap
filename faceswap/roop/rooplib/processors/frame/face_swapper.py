import threading
from typing import Any, Callable

import cv2
import insightface
from rooplib import config
from rooplib.core import update_status
from rooplib.face_analyser import find_similar_face, get_one_face
from rooplib.face_reference import (
    clear_face_reference,
    get_face_reference,
    set_face_reference,
)
from rooplib.processors.frame import core
from rooplib.typing import Face, Frame
from rooplib.utilities import (
    conditional_download,
    decode_execution_providers,
    is_image,
    is_video,
    resolve_relative_path,
)

FACE_SWAPPER = None
THREAD_LOCK = threading.Lock()
NAME = "ROOP.FACE-SWAPPER"


def get_face_swapper() -> Any:
    global FACE_SWAPPER

    with THREAD_LOCK:
        if FACE_SWAPPER is None:
            model_path = resolve_relative_path("../models/inswapper_128.onnx")
            FACE_SWAPPER = insightface.model_zoo.get_model(
                model_path,
                providers=decode_execution_providers(
                    config.execution_providers
                ),
            )
    return FACE_SWAPPER


def clear_face_swapper() -> None:
    global FACE_SWAPPER

    FACE_SWAPPER = None


def pre_check() -> bool:
    update_status(
        "Running rooplib.processors.frame.face_swapper.pre_check", NAME
    )
    download_directory_path = resolve_relative_path("../models")
    conditional_download(
        download_directory_path,
        [
            "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
        ],
    )
    return True


def pre_start(source_path: str, target_path: str) -> bool:
    update_status(
        "Running rooplib.processors.frame.face_swapper.pre_start", NAME
    )
    if not is_image(source_path):
        update_status("Select an image for source path.", NAME)
        raise Exception("Select an image for source path.")
    if not get_one_face(cv2.imread(source_path)):
        update_status("Face not found on source image", NAME)
        raise Exception("Face not found on source image")
    if not is_image(target_path) and not is_video(target_path):
        update_status("Select an image or video for target path.", NAME)
        raise Exception("Select an image or video for target path.")
    return True


def post_process() -> None:
    clear_face_swapper()
    clear_face_reference()


def swap_face(
    source_face: Face, target_face: Face, temp_frame: Frame
) -> Frame:
    return get_face_swapper().get(
        temp_frame, target_face, source_face, paste_back=True
    )


def process_frame(
    source_face: Face, reference_face: Face, temp_frame: Frame
) -> Frame:
    target_face = find_similar_face(temp_frame, reference_face)
    if target_face:
        temp_frame = swap_face(source_face, target_face, temp_frame)
    return temp_frame


def process_frames(
    source_path: str, temp_frame_paths: list[str], update: Callable[[], None]
) -> None:
    source_face = get_one_face(cv2.imread(source_path))
    reference_face = get_face_reference()
    for temp_frame_path in temp_frame_paths:
        temp_frame = cv2.imread(temp_frame_path)
        result = process_frame(source_face, reference_face, temp_frame)
        cv2.imwrite(temp_frame_path, result)
        if update:
            update()


def process_video(source_path: str, temp_frame_paths: list[str]) -> None:
    reference_frame = cv2.imread(
        temp_frame_paths[config.reference_frame_number]
    )
    reference_face = get_one_face(reference_frame)
    set_face_reference(reference_face)
    core.process_video(source_path, temp_frame_paths, process_frames)
