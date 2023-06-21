from django.urls import path

from game import views


app_name = 'game'

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),


]
