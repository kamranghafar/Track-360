from django.urls import path
from . import views

app_name = 'ai_agent'

urlpatterns = [
    # Chat interface
    path('chat/', views.chat_view, name='chat'),
    path('chat/embed/', views.chat_embed_view, name='chat_embed'),
    path('chat/history/', views.ChatHistoryView.as_view(), name='chat_history'),

    # API endpoints
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/end-chat/', views.end_chat, name='end_chat'),
    path('api/new-chat/', views.new_chat, name='new_chat'),
]
