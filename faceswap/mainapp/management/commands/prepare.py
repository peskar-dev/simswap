from django.core.management.base import BaseCommand
from mainapp.models import Video

from roop.rooplib.core import prepare


class Command(BaseCommand):

    def handle(self, *args, **options):
        video_path = Video.related_video_path()
        prepare(video_path)
