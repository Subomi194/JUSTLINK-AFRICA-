from django.urls import path
from chats.views import ConversationListView

urlpatterns = [
    path('conversations/list/', ConversationListView.as_view(), name='conversation-list'),
]