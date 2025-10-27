from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_audio, name='upload_audio'),
]
