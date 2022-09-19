from django.contrib.auth import views as auth_views
from django.urls import path

from game import views
from game.forms import UserLoginForm


app_name = 'game'

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),

    # Authentication
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            authentication_form=UserLoginForm,
            template_name='game/login.html',
            next_page='game:profile',
        ),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='game:login'), name='logout'),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/verify_message/', views.SignUpView.as_view(), name='verify_message'),

    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),

    path('accounts/password-change/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_change'),
    path('accounts/password-change/done/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_change_done'),
    path('accounts/password_reset/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.LoginView.as_view(template_name='game/login.html'), name='password_reset_complete'),
]
