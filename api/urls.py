from django.urls import path
from django.urls.conf import include

from api import views

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('profile/', views.ProfileViewSet.as_view({'get': 'retrieve'}), name='user'),
    path('users/', views.UserListViewSet.as_view({'get': 'list'}), name='user'),

    path('play/', views.GameViewSet.as_view({
        'get': 'get_chan_attempt',
        'post': 'get_answer_result',
    }), name='user'),
]
