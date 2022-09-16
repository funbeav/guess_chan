from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib import admin
from .managers import UserManager


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """ User model: identification by email, additional fields: first_name, last_name, father_name. """
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    login = models.CharField(max_length=30, unique=True, verbose_name=_('Login'))

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        ordering = ('login',)

    def __str__(self):
        return f'{self.login}'
