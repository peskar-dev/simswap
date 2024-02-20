from celery import shared_task
import subprocess
from .models import GPU
import pycuda.driver as cuda

@shared_task
def process_photo_task(photo_path, dirkey, gpuid):
    try:
        gpu = GPU.objects.get(id=gpuid)
        gpu_device = cuda.Device(gpu.device_info)
        with gpu_device.make_context() as context:
            command = f"cd ../roop || python run.py --execution-provider cuda -s {photo_path} -t ./VS{gpuid}.mp4 -o ../mainapp/outputs/{dirkey}"
            subprocess.run(command, shell=True, check=True)
            gpu.counter += 1
            gpu.save()
    except Exception as e:
        print(f"An error occurred: {e}")