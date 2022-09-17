from django.urls import path
from django.urls.conf import include

from api import views

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('profile/', views.ProfileViewSet.as_view({'get': 'retrieve'}), name='user'),
    path('users/', views.UserListViewSet.as_view({'get': 'list'}), name='user'),
]
