from django.core.management.base import BaseCommand
from mainapp.models import GPU
from pycuda.compiler import SourceModule  

import pycuda.driver as cuda
import pycuda.autoinit

class Command(BaseCommand):
    help = 'Update GPU data in the database'

    def handle(self, *args, **options):
        GPU.objects.all().delete()

        cuda.init()
        num_gpus = cuda.Device.count()

        for i in range(num_gpus):
            gpu = cuda.Device(i)
            print(gpu.pci_bus_id())
            GPU.objects.create(device_info=gpu.pci_bus_id(), counter=0)

        self.stdout.write(self.style.SUCCESS('Successfully updated GPU data in the database'))
