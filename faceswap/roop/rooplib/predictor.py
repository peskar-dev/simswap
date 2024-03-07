import threading

import opennsfw2

PREDICTOR = None
THREAD_LOCK = threading.Lock()
MAX_PROBABILITY = 0.85


def predict_video(target_path: str) -> bool:
    _, probabilities = opennsfw2.predict_video_frames(
        video_path=target_path, frame_interval=100
    )
    return any(probability > MAX_PROBABILITY for probability in probabilities)
