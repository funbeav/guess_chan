import os
import uuid

import imagehash
from PIL import Image
from django.db import models

from project.models import Lang


def generate_filename(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(f'images/{instance.folder}', f'{uuid.uuid4()}.{ext}')


class BaseImage(models.Model):
    image = models.ImageField(upload_to=generate_filename)
    caption = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True, default='Unknown')
    hash = models.CharField(max_length=20, blank=True, unique=True)

    def save(self, *args, **kwargs):
        self.hash = str(imagehash.average_hash(Image.open(getattr(self.image, 'file'))))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or self.hash


class Character(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class CharacterImage(BaseImage):
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def folder(self):
        return 'character'


class Chan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    character = models.OneToOneField(Character, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class ChanImage(BaseImage):
    chan = models.ForeignKey(Chan, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def folder(self):
        return 'chan'


class CharacterName(models.Model):
    """ Acceptable Character's names """

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.character.name} ~ {self.name}'
