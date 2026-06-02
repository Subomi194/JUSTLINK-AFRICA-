from django.urls import path
from lawyers.views import LawyerListView

urlpatterns = [
    path('browse-lawyers/', LawyerListView.as_view(), name='lawyer-list'),
]