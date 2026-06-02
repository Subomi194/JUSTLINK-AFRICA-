from django.urls import path
from chats.views import StartConversationView, ConversationListView

urlpatterns = [
    path('conversations/', StartConversationView.as_view(), name='start-conversation'),
    path('conversations/list/', ConversationListView.as_view(), name='conversation-list'),
]