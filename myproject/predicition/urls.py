from django.urls import path
from .views import weather_prediction_model

urlpatterns = [
    path('',weather_prediction_model, name='weather_prediction_model'),
]