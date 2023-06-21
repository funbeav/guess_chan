from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, UserChangeForm, \
    PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import NumericPasswordValidator
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from django import forms
from django.forms import EmailField, ImageField, BooleanField

from guess_chan.settings import ALLOWED_EXTENSIONS
from project.models import User


def validate_password_strength(value):
    min_length = 5

    if len(value) < min_length:
        raise ValidationError(_('Password must be at least {0} characters long.').format(min_length))

    if value.isdigit():
        raise ValidationError(
            _("This password is entirely numeric."),
            code="password_entirely_numeric",
        )

    if sum(c.isdigit() for c in value) < 1:
        raise ValidationError(_('Password must container at least 1 digit.'))
    return value


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)


class UserSignupForm(UserCreationForm):
    login = UsernameField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}))
    email = EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            "autocomplete": "new-password",
            'placeholder': 'Password'
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("login", "email",)

    def clean_password1(self):
        return validate_password_strength(self.cleaned_data['password1'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2


class UserProfileForm(UserChangeForm):
    login = UsernameField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}))
    email = EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    image = ImageField(widget=forms.FileInput(
        attrs={'class': 'form-control form-control-sm', 'type': 'file', 'onchange': 'preview()', 'id': 'upload'}),
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)]
    )

    class Meta:
        model = User
        fields = ("login", "email", "image",)

    def clean_image(self):
        if 'image' in self.changed_data:
            if self.instance.image: self.instance.image.delete()
        image = self.cleaned_data.get('image')
        return image


class UserPasswordResetForm(PasswordResetForm):
    email = EmailField(widget=forms.EmailInput(attrs={'class': 'form-control text-center', 'placeholder': 'Email'}))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            "autocomplete": "new-password",
            'placeholder': 'New Password'
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_new_password1(self):
        return validate_password_strength(self.cleaned_data['new_password1'])

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2


class UserPasswordChangeForm(UserSetPasswordForm):
    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            "autocomplete": "new-password",
            'placeholder': 'Old Password',
        }),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password
