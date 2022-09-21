from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic
from verify_email import send_verification_email

from project.forms import UserSignupForm, UserProfileForm, UserPasswordResetForm
from project.models import User


def verify_info(request):
    return render(request, 'project/verify/info.html')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = UserPasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "project/password/reset_email_msg.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("project:password_reset_done")
            else:
                password_reset_form.add_error('email', 'Invalid Email')
        return render(
            request=request,
            template_name="project/password/reset.html",
            context={"password_reset_form": password_reset_form}
        )
    password_reset_form = UserPasswordResetForm()
    return render(
        request=request,
        template_name="project/password/reset.html",
        context={"password_reset_form": password_reset_form}
    )


class SignUpView(generic.CreateView):
    form_class = UserSignupForm
    template_name = "project/signup.html"

    def __init__(self, **kwargs):
        self.object = None
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            send_verification_email(request, form)
            return redirect('verify_info')
        else:
            return self.form_invalid(form)


class ProfileView(generic.UpdateView):
    form_class = UserProfileForm
    success_url = reverse_lazy("project:profile")
    template_name = "project/profile.html"
    queryset = User.objects.all()

    def get_object(self, queryset=None):
        obj = self.queryset.get(pk=self.request.user.id)
        return obj
