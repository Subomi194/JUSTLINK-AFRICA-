from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer, LawyerSerializer, CustomTokenObtainPairSerializer, UserLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
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

        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)    
        
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

class UsersProfileView(APIView):
    serializer_class = UserSerializer

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response({'data': serializer.data, 'message': 'User profile retrieved successfully.' }, status=status.HTTP_200_OK)