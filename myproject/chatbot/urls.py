from django.urls import path
from .views import chatbot_model, clear_chat

urlpatterns = [
    path('',chatbot_model, name='chatbot_model_1'),
    path('clear-chat/',clear_chat, name='clear_chat')
]