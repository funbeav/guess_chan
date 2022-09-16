from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique id
    for authentication instead of login(username).
    """
    def create_user(self, login, password, **kwargs):
        """
        Create and save a User with the given email, password and kwargs.
        """
        if not login: raise ValueError(_('Login is missing'))
        user = self.model(login=login, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login, password, **kwargs):
        """
        Create and save a SuperUser with the given login, password and kwargs.
        """
        return self.create_user(login, password, **kwargs, is_staff=True, is_superuser=True)
