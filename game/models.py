from django.core.files.storage import FileSystemStorage
from django.db import models


class ChanImage(models.Model):
    caption = models.CharField(max_length=200)
    author = models.CharField(max_length=200, default='Unknown')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.caption
