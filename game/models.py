import imagehash
from PIL import Image
from django.db import models

from common.utils import generate_filename
from project.models import Lang


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
    def image_folder(self):
        return 'character'


class Chan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    character = models.OneToOneField(Character, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class ChanImage(BaseImage):
    chan = models.ForeignKey(Chan, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def image_folder(self):
        return 'chan'


class CharacterName(models.Model):
    """ Acceptable Character's names """

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.character.name} ~ {self.name}'
