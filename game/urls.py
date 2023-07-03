from django.urls import path

from game import views


app_name = 'game'

urlpatterns = [
    path('', views.index, name='home'),
    path('logs/', views.logs, name='logs'),
    path('show_correct/', views.show_correct, name='show_correct'),

]
