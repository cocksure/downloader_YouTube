from django.urls import path
from . import views

urlpatterns = [
    path('downloader/', views.download_page, name='download_page'),
    path('progress/', views.get_progress, name='get_progress'),
]
