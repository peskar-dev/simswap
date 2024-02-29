from django.shortcuts import render, redirect
from django.http import FileResponse,HttpResponse
import subprocess
from .forms import ImageUploadForm
from mainapp.models import GPU
from .models import Video
import uuid
import os
import time
import threading
import multiprocessing
import logging
import shutil
from pathlib import Path
import pycuda.driver as cuda

lock = multiprocessing.RLock()
def home(request):
    videos = Video.objects.filter(show=True)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ImageUploadForm()
    return render(request, 'home.html', {'videos': videos, 'form': form})
#queue_name = f'render_queue_gpu_{gpuid}'


def process_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        #takes file path
        photo_file = request.FILES['photo']
        photo_path = photo_file.temporary_file_path()
        
        #generating unique key and make dir with that key
        dirkey = uuid.uuid4().hex.lower()[0:6]
        subprocess.run(f'mkdir ./outputs/{dirkey}', shell=True)
        output_path = os.path.abspath(f'./outputs/{dirkey}')
        

        #TODO: Сделать подтягивание видика загруженного в бд (я чет не вкурил как)
        video_obj = Video.objects.filter(show=True).first()
        video_file = video_obj.video_file
        video_path = Path(video_file.path) 
        new_video_path = Path(f'./mainapp/outputs/{dirkey}.mp4')
        shutil.copyfile(video_path, new_video_path)

        #get least used gpu and run render in gpu context

        multiprocessing.Process(target=cuda_render, args=(photo_path, output_path, new_video_path, lock,)).start()
        
        return redirect('result')
    return render(request, 'photo.html')

def download_photo(dirkey):
    directory = f'./outputs/{dirkey}'
    video_file_path = os.path.join(directory, 'output.mp4')  
    
    if os.path.exists(video_file_path):
        with open(video_file_path, 'rb') as video_file:
            response = FileResponse(video_file)
            response['Content-Type'] = 'video/mp4'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_file_path)}"'
            threading.Thread(target=delete_directory, args=(f'outputs/{dirkey}',), name='folder_deletion').start()
            return response
    else:
        return HttpResponse(status=404)

def delete_directory(directory):
    time.sleep(300)  
    if os.path.exists(directory):
        os.system(f'rm -rf {directory}')

def cuda_render(photo_path, gpu_device, output_path, new_video_path, lock):
    lock.acquire()
    cuda.init()
    gpu = GPU.objects.order_by('counter').first()
    gpuid = gpu.id
    gpu = GPU.objects.get(id=gpuid)
    gpu_device = cuda.Device("00000000:01:00.0")

    with gpu_device.make_context() as context:
        command = f"cd ./roop || python run.py --execution-provider cuda -s {photo_path} -t {new_video_path} -o {output_path}"
        gpu.counter += 1
        gpu.save()
        subprocess.check_call(command, shell=True)
    lock.realease()