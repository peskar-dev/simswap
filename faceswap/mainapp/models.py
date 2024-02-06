from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/')
    show = models.BooleanField(default=False) 

    def __str__(self):
        return self.title

class Image(models.Model):
    title = models.CharField(max_length=200)
    image_file = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

class GPU(models.Model):
    device_info = models.CharField(max_length=250)
    counter = models.IntegerField()

    def __str__(self):
        return self.title
