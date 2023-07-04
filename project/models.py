from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django_resized import ResizedImageField

from common.utils import generate_filename
from game.constants import DEFAULT_LANG
from guess_chan.settings import LOGO_RESOLUTION
from .managers import UserManager


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Lang(models.Model):
    alpha2 = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} ({self.alpha2})'


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """User model: identification by email, username field: login"""
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    login = models.CharField(max_length=30, unique=True, verbose_name=_('Login'))

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_always_show_correct_answer = models.BooleanField(default=False)

    image = ResizedImageField(
        upload_to=generate_filename, null=True, blank=True,
        size=[LOGO_RESOLUTION, LOGO_RESOLUTION],
    )
    energy = models.IntegerField(default=10)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    @property
    def image_folder(self):
        return 'user'

    def change_energy(self, energy: int):
        self.energy += energy
        self.save()

    def save(self, *args, **kwargs):
        if not self.lang:
            self.lang = Lang.objects.get(alpha2=DEFAULT_LANG)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.login}'
