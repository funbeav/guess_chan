import os
import uuid

import imagehash
from PIL import Image
from django.db import models

from project.models import Lang


def generate_filename(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('images', f'{uuid.uuid4()}.{ext}')


class Chan(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class ChanImage(models.Model):
    image = models.ImageField(upload_to=generate_filename)
    chan = models.ForeignKey(Chan, null=True, blank=True, on_delete=models.SET_NULL)
    caption = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True, default='Unknown')
    hash = models.CharField(max_length=20, blank=True, unique=True)

    def save(self, *args, **kwargs):
        self.hash = str(imagehash.average_hash(Image.open(getattr(self.image, 'file'))))
        super(ChanImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.caption or self.hash


class ChanAlternative(models.Model):
    """ Model for alternative Chan's correct names"""

    chan = models.ForeignKey(Chan, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True)
