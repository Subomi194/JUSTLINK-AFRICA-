from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer, LawyerSerializer, CustomTokenObtainPairSerializer, UserLoginSerializer, LawyerProfileEditSerializer, AllUsersProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema

User = get_user_model()

# Create your views here.

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'data': UserSerializer(user).data, 'message': 'User created successfully.' }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LawyerRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LawyerSerializer

    @extend_schema(request=LawyerSerializer, responses={201: LawyerSerializer})
    def post(self, request):
        serializer = LawyerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'data': LawyerSerializer(user).data, 'message': 'Lawyer created successfully.' }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(request=UserLoginSerializer, responses={200: CustomTokenObtainPairSerializer})
    def post(self, request):

        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({'error': 'Invalid phone number or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid phone number or password.'}, status=status.HTTP_401_UNAUTHORIZED)    
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'name': user.name,
                'role': user.role,
                'country': user.country,
                'language': user.language,
            }
        }, status=status.HTTP_200_OK)

class AllUsersProfileView(APIView):
    serializer_class = AllUsersProfileSerializer

    @extend_schema(responses={200: AllUsersProfileSerializer})
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response({'data': serializer.data, 'message': 'User profile retrieved successfully.' }, status=status.HTTP_200_OK)

class USSDView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        session_id = request.data.get('ussd_session_id')
        phone_number = request.data.get('phone_number')
        text = request.data.get('text', '')

        if text == '':
            response = "CON Welcome to JustLink Africa\n"
            response += "1. Know your rights\n"
            response += "2. Get legal help\n"
            response += "3. Find a lawyer"

        elif text == '1':
            response = "CON Select a topic\n"
            response += "1. Labour rights\n"
            response += "2. Land rights\n"
            response += "3. Domestic violence"

        elif text == '1*1':
            response = "END You have the right to a written\n"
            response += "contract and minimum wage."

        elif text == '2':
            response = "END Your case has been logged.\n"
            response += "A lawyer will contact you soon."

        else:
            response = "END Invalid option. Please try again."

        return HttpResponse(response, content_type='text/plain')


class LawyerProfileEditView(APIView):
    serializer_class = LawyerProfileEditSerializer

    @extend_schema(request=LawyerProfileEditSerializer, responses={200: LawyerProfileEditSerializer})

    def patch(self, request):
        if request.user.role != 'lawyer':
            return Response({'error': 'Only lawyers can edit their profiles.'}, status=status.HTTP_403_FORBIDDEN)
        
        profile = request.user.lawyer_profile
        
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'message': 'Lawyer profile updated successfully.' }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)