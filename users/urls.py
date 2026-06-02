from django.urls import path
from users.views import UserRegistrationView, LawyerRegistrationView, AllUsersProfileView, LawyerProfileEditView

urlpatterns = [
    path('register/user/', UserRegistrationView.as_view(), name='user-register'),
    path('register/lawyer/', LawyerRegistrationView.as_view(), name='lawyer-register'),
    path('profile/', AllUsersProfileView.as_view(), name='all-users-profile'),
    path('lawyer/profile/edit/', LawyerProfileEditView.as_view(), name='lawyer-profile-edit'),
]