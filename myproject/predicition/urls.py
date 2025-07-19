from django.urls import path
from .views import weather_prediction_model, plot_png

urlpatterns = [
    path('',weather_prediction_model, name='weather_prediction_model'),
    path('plot/', plot_png, name='plot_png'),
]