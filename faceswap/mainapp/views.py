import logging
import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from mainapp.models import GPU

from .forms import ImageUploadForm
from .models import Video

lock = threading.RLock()

logger = logging.getLogger(__name__)


def home(request):
    videos = Video.objects.filter(show=True)
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ImageUploadForm()
    return render(request, "home.html", {"videos": videos, "form": form})


# queue_name = f'render_queue_gpu_{gpuid}'


def process_photo(request):
    if request.method == "POST" and request.FILES.get("photo"):
        logger.debug("Received POST request")
        dirkey = uuid.uuid4().hex.lower()[0:6]
        logger.debug(f"Will create temporary directory: {dirkey}")
        BASE_DIR = Path(__file__).resolve().parent
        output_path = os.path.join(BASE_DIR, "outputs", dirkey)
        logger.debug(f"Creating temporary directory: {output_path}")
        os.makedirs(output_path, exist_ok=True)

        photo_file = request.FILES["photo"]
        img_ext = Path(photo_file.name).suffix

        logger.debug(f"Received photo file: {photo_file}")

        photo_path = os.path.join(output_path, f"photo{img_ext}")

        with open(photo_path, "wb") as output_file:
            for chunk in photo_file.chunks():
                output_file.write(chunk)

        logger.debug(f"Saved photo file: {photo_path}")

        video_obj = Video.objects.filter(show=True).first()
        logger.debug(f"Using video object: {video_obj}")
        video_file = video_obj.video_file
        video_path = Path(video_file.path)
        new_video_path = Path(f"{output_path}/copyvid.mp4")
        logger.debug(f"Will save video file: {new_video_path}")
        shutil.copyfile(video_path, new_video_path)
        logger.debug(f"Copied video file: {new_video_path}")

        MAIN_DIR = Path(__file__).resolve().parent.parent
        roop_dir = MAIN_DIR / "roop"

        logger.info(f"s = {photo_path}")
        logger.info(f"t = {new_video_path}")
        logger.info(f"o = {output_path}")

        with ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="render_queue"
        ) as pool:
            rend = pool.submit(
                cuda_render, photo_path, output_path, new_video_path, roop_dir
            )
        # threading.Thread(target=cuda_render, args=(photo_path, output_path, new_video_path, gpu_device,roop_dir,), name=f'render_{gpuid}').start()

        return redirect("result", dirkey=dirkey)
    return redirect("uploading_photos")


def download_photo(request, dirkey):
    BASE_DIR = Path(__file__).resolve().parent
    directory = os.path.join(BASE_DIR, "outputs", dirkey)
    video_file_path = os.path.join(directory, "result.mp4")
    logger.debug(f"Searching for video file: {video_file_path}")

    if os.path.exists(video_file_path):
        logger.debug(f"Found video file: {video_file_path}")
        response = FileResponse(open(video_file_path, "rb"))
        response["Content-Type"] = "video/mp4"
        response["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(video_file_path)}"'
        )
        threading.Thread(target=delete_directory, args=(directory,)).start()
        return response
    logger.debug(f"No video file found: {video_file_path}")
    return HttpResponse(status=404)


def delete_directory(directory):
    print(directory)
    time.sleep(60)
    shutil.rmtree(directory)


def cuda_render(photo_path, output_path, new_video_path, roop_dir):
    #     gpu = GPU.objects.order_by('counter').first()
    #     if(!gpu):
    #         subprocess.check_call('')
    # -   gpuid = gpu.id

    # -   cuda.init()
    # -   gpu_device = cuda.Device(gpu.device_info)
    time.sleep(2)
    logger.debug(f"Rendering {photo_path}")
    command = f"python3 run.py --execution-provider cuda -s {photo_path} -t {new_video_path} -o {output_path}/result.mp4 --frame-processor face_swapper --keep-frames --reference-frame-number 31"
    logger.debug(f"Command: {command}")
    subprocess.check_call(command, shell=True, cwd=roop_dir)
    return 1
