from django.contrib.auth import views as auth_views
from django.urls import path

from project import views
from project.forms import UserLoginForm


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
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('password-change/', auth_views.LoginView.as_view(template_name='project/login.html'), name='password_change'),
    path('password-change/done/', auth_views.LoginView.as_view(template_name='project/login.html'), name='password_change_done'),
    path('password_reset/done/', auth_views.LoginView.as_view(template_name='project/login.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.LoginView.as_view(template_name='project/login.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.LoginView.as_view(template_name='project/login.html'), name='password_reset_complete'),
]
