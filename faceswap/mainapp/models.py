from django.db import models


class VideoGenerationCount(models.Model):
    count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def increment_count(cls):
        obj = cls.load()
        obj.count += 1
        obj.save()


class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to="videos/")
    show = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @classmethod
    def related_video_path(cls) -> str:
        video_instance = cls.objects.filter(show=True).first()
        return video_instance.video_file.path


class Image(models.Model):
    title = models.CharField(max_length=200)
    image_file = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.title


class GPU(models.Model):
    device_info = models.CharField(max_length=250)
    counter = models.IntegerField()

    def __str__(self):
        return self.title
