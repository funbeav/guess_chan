from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django import forms
from django.forms import EmailField, ImageField, BooleanField

from project.models import User


def validate_password_strength(value):
    min_length = 5

    if len(value) < min_length:
        raise ValidationError(_('Password must be at least {0} characters long.').format(min_length))

    # check for 1 digits
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
        attrs={'class': 'form-control form-control-sm', 'type': 'file'}),
        required=False,
    )
    is_save_image = BooleanField(widget=forms.CheckboxInput(
        attrs={'checked': True, 'class': 'form-check-input mt-0', 'type': 'checkbox'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ("login", "email", "image",)
