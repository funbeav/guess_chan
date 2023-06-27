from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from project import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('project.urls'), name='project'),
    path('verification/info/', project_views.verify_info, name='verify_info'),
    path('verification/', include('verify_email.urls')),
    path('api/', include('api.urls'), name='api'),

    path('', include('game.urls'), name='game'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
