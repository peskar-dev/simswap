import threading

import insightface
import numpy
from roop.rooplib import config
from roop.rooplib.typing import Face, Frame
from roop.rooplib.utilities import decode_execution_providers

FACE_ANALYSER = None
THREAD_LOCK = threading.Lock()


def get_face_analyser() -> any:
    global FACE_ANALYSER

    with THREAD_LOCK:
        if FACE_ANALYSER is None:
            FACE_ANALYSER = insightface.app.FaceAnalysis(
                name="buffalo_l",
                providers=decode_execution_providers(["cuda", "coreml"]),
            )
            FACE_ANALYSER.prepare(ctx_id=0)
    return FACE_ANALYSER


def get_one_face(frame: Frame, position: int = 0) -> Face | None:
    many_faces = get_many_faces(frame)
    if many_faces:
        try:
            return many_faces[position]
        except IndexError:
            return many_faces[-1]
    return None


def get_many_faces(frame: Frame) -> list[Face] | None:
    try:
        return get_face_analyser().get(frame)
    except ValueError:
        return None


def find_similar_face(frame: Frame, reference_face: Face) -> Face | None:
    many_faces = get_many_faces(frame)
    if many_faces:
        for face in many_faces:
            if hasattr(face, "normed_embedding") and hasattr(
                reference_face, "normed_embedding"
            ):
                distance = numpy.sum(
                    numpy.square(
                        face.normed_embedding - reference_face.normed_embedding
                    )
                )
                if distance < config.similar_face_distance:
                    return face
    return None
