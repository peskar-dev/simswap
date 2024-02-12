from django.shortcuts import render, redirect
from django.http import FileResponse,HttpResponse
import subprocess
import pycuda.driver as cuda
from .forms import ImageUploadForm
from mainapp.models import GPU
from .models import Video
import uuid
import os
import time
import threading

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

def process_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        #takes file path
        photo_file = request.FILES['photo']
        photo_path = photo_file.temporary_file_path()
        
        #generating unique key and make dir with that key
        dirkey = uuid.uuid4().hex.lower()[0:6]
        subprocess.run(f'mkdir ./outputs/{dirkey}', shell=True, capture_output=True, text=True)
        
        #get least used gpu and run render in gpu context
        gpu = GPU.objects.order_by('counter').first()
        gpu_device = cuda.Device(gpu.device_info)
        
        with gpu_device.make_context() as context:
            command = f"cd ../roop || python run.py --execution-provider cuda -s {photo_path} -t ./VS.mp4 -o ./outputs "  
            process = subprocess.run(command, shell=True, capture_output=True, text=True)

        
        gpu.counter +=1
        gpu.save()
        return redirect('result', key=dirkey)
    return render(request, 'result.html')

def download_photo(dirkey):
    directory = f'./outputs/{dirkey}'
    video_file_path = os.path.join(directory, 'output.mp4')  
    
    if os.path.exists(video_file_path):
        with open(video_file_path, 'rb') as video_file:
            response = FileResponse(video_file)
            response['Content-Type'] = 'video/mp4'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_file_path)}"'
            threading.Thread(target=delete_directory, args=(f'outputs/{dirkey}',)).start()
            return response
    else:
        return HttpResponse(status=404)

def delete_directory(directory):
    time.sleep(300)  
    if os.path.exists(directory):
        os.system(f'rm -rf {directory}')