from django.conf.urls.static import static 
from django.conf import settings
from .import views
from django.urls import path




urlpatterns = [
     path('', views.index, name='index'),

]


if settings.DEBUG:
# Serve static and media files during development
     urlpatterns +=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) 
     urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)