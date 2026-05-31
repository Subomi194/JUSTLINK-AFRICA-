from django.urls import path
from users.views import UserRegistrationView, LawyerRegistrationView, UsersProfileView

urlpatterns = [
    path('register/user/', UserRegistrationView.as_view(), name='user-register'),
    path('register/lawyer/', LawyerRegistrationView.as_view(), name='lawyer-register'),
    path('profile/', UsersProfileView.as_view(), name='user-profile'),
]