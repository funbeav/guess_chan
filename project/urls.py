from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from project import views
from project.forms import UserLoginForm, UserSetPasswordForm, UserPasswordChangeForm

app_name = 'project'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            authentication_form=UserLoginForm,
            template_name='project/login.html',
            next_page='project:profile',
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='project:login'), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('password_reset/', views.password_reset_request, name='password_reset'),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='project/password/reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=UserSetPasswordForm,
            template_name='project/password/reset_confirm.html',
            success_url=reverse_lazy("project:password_reset_complete"),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='project/password/reset_complete.html'),
        name='password_reset_complete',
    ),
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(
            form_class=UserPasswordChangeForm,
            template_name='project/password/change.html',
            success_url=reverse_lazy("project:password_change_done"),
        ),
        name='password_change'
    ),
    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='project/password/change_done.html',
        ),
        name='password_change_done',
    ),
]
