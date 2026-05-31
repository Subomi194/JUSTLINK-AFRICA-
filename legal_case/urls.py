from django.urls import path
from legal_case.views import LegalCaseView

urlpatterns = [
    path('my-cases/', LegalCaseView.as_view(), name='legal-case'),
]