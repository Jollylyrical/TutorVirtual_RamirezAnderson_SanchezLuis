from django.urls import path

from .views import AskTutorView, ConversationHistoryView

urlpatterns = [
    path('ask/', AskTutorView.as_view(), name='ask_tutor'),
    path('history/', ConversationHistoryView.as_view(), name='conversation_history'),
]
