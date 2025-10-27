from django.urls import path
from . import views

urlpatterns = [
    path('api/predict', views.predict_api, name='api_predict'),
    path('', views.upload_audio, name='upload_audio'),
]
