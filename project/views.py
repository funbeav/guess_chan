from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from verify_email import send_verification_email

from project.forms import UserSignupForm, UserProfileForm
from project.models import User


def verify_info(request):
    return render(request, 'project/verify/info.html')


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
