from django.urls import path
from legal_case.views import LawyerConnectView, CaseRespondView

urlpatterns = [
    path('my-connects/', LawyerConnectView.as_view(), name='lawyer-connect'),
    path('respond/<int:case_id>/', CaseRespondView.as_view(), name='case-respond'),
]