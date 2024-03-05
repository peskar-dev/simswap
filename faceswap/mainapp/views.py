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
from concurrent.futures import ThreadPoolExecutor
import shutil
from pathlib import Path
import tempfile 


lock = threading.RLock()
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
        dirkey = uuid.uuid4().hex.lower()[0:6]
        BASE_DIR = Path(__file__).resolve().parent
        output_path = os.path.join(BASE_DIR, "outputs", dirkey)
        subprocess.run(f'mkdir -p {output_path}', shell=True)

        photo_file = request.FILES['photo']
        img_ext = Path(photo_file.name).suffix

        photo_path = os.path.join(output_path, f"photo{img_ext}")

        with open(photo_path, 'wb') as output_file:
            for chunk in photo_file.chunks():
                output_file.write(chunk)
        
            #generating unique key and make dir with that key
        
        video_obj = Video.objects.filter(show=True).first()
        video_file = video_obj.video_file
        video_path = Path(video_file.path) 
        new_video_path = Path(f'{output_path}/copyvid.mp4')
        shutil.copyfile(video_path, new_video_path)
        
        
        MAIN_DIR = Path(__file__).resolve().parent.parent 
        roop_dir = MAIN_DIR / "roop"
        
        
        print(f's = {photo_path}')
        print(f't = {new_video_path}')
        print(f'o = {output_path}')  

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix='render_queue') as pool:
            rend = pool.submit(cuda_render, photo_path, output_path, new_video_path, roop_dir)
        # threading.Thread(target=cuda_render, args=(photo_path, output_path, new_video_path, gpu_device,roop_dir,), name=f'render_{gpuid}').start()

              
        return redirect('result', dirkey=dirkey)

def download_photo(request, dirkey):
    BASE_DIR = Path(__file__).resolve().parent
    directory = os.path.join(BASE_DIR, "outputs", dirkey)
    video_file_path = os.path.join(directory, 'result.mp4')  
    
    if os.path.exists(video_file_path):

        response = FileResponse(open(video_file_path, 'rb'))
        response['Content-Type'] = 'video/mp4'
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_file_path)}"'
        threading.Thread(target=delete_directory, args=(directory,)).start()
        return response


def delete_directory(directory):
    print(directory)
    time.sleep(180)  
    shutil.rmtree(directory)

def cuda_render(photo_path, output_path, new_video_path, roop_dir):
#     gpu = GPU.objects.order_by('counter').first()
#     if(!gpu):
#         subprocess.check_call('')
# -   gpuid = gpu.id

# -   cuda.init()
# -   gpu_device = cuda.Device(gpu.device_info)
    time.sleep(2)
    command = f"python3 run.py --execution-provider cuda -s {photo_path} -t {new_video_path} -o {output_path}/result.mp4 --frame-processor face_swapper --keep-frames --reference-frame-number 31"
    subprocess.check_call(command, shell=True, cwd=roop_dir)
    return 1
    
    
