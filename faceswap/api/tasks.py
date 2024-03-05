from faceswap.celery import app


@app.task
def generate_faceswap(file_path: str):
    pass
