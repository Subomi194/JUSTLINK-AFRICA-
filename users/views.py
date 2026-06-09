from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from users.models import User
from users.serializers import (
    UserSerializer, 
    LawyerSerializer, 
    CustomTokenObtainPairSerializer, 
    UserLoginSerializer, 
    LawyerProfileEditSerializer, 
    AllUsersProfileSerializer
)
from legal_case.models import LegalCase
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from users.utils import normalize_phone


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
        phone_number = normalize_phone(request.data.get('phone_number'))
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

class USSDView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        session_id = request.data.get('sessionId')
        phone_number = request.data.get('phoneNumber')
        text = request.data.get('text', '')

        print("USSD phone:", repr(phone_number))

        # try to find existing user by phone number
        try:
            user = User.objects.get(phone_number=phone_number)
            # update their ussd session id
            user.ussd_session_id = session_id
            user.save()
            print("FOUND USER:", user.id, user.phone_number)
            is_registered = True
        except User.DoesNotExist:
            print("USER NOT FOUND")

            print(
                list(
                    User.objects.values_list(
                        "phone_number",
                        flat=True
                    )
                )
            )
            is_registered = False

        print(request.data)            

        if text == '':
            if is_registered:
                response = f"CON Welcome back {user.name}.\n"
            else:
                response = "CON Welcome to JustLink Africa.\n"
            response += "1. Know your rights\n"
            response += "2. Get legal help\n"
            response += "3. Find a lawyer"
            response += "4. About JustLink"

        elif text == '1':
            response = "CON Select a legal topic:\n"
            response += "1. Labour rights\n"
            response += "2. Land & property\n"
            response += "3. Family & inheritance\n"
            response += "4. Domestic violence\n"
            response += "5. Police abuse"

        elif text == '1*1':
            response = "END LABOUR RIGHTS:\n"
            response += "You have the right to:\n"
            response += "- Written employment contract\n"
            response += "- Minimum wage\n"
            response += "- 30 days notice before termination\n"
            response += "Dial again for more help."

        elif text == '1*2':
            response = "END LAND RIGHTS:\n"
            response += "You have the right to:\n"
            response += "- Certificate of Occupancy\n"
            response += "- Fair compensation if land acquired\n"
            response += "- Challenge illegal eviction in court.\n"
            response += "Dial again for more help."

        elif text == '1*3':
            response = "END FAMILY & INHERITANCE:\n"
            response += "You have the right to:\n"
            response += "- Contest an unfair will\n"
            response += "- Spousal property rights\n"
            response += "- Child custody rights.\n"
            response += "Dial again for more help."

        elif text == '1*4':
            response = "END DOMESTIC VIOLENCE:\n"
            response += "You are not alone.\n"
            response += "- You can get a restraining order\n"
            response += "- Report to nearest police station\n"
            response += "- Call 112 for emergency help.\n"
            response += "Dial again to find a lawyer."

        elif text == '1*5':
            response = "END POLICE ABUSE:\n"
            response += "You have the right to:\n"
            response += "- Know why you are arrested\n"
            response += "- Legal representation\n"
            response += "- Remain silent until lawyer present.\n"
            response += "Dial again to get legal help."

        elif text == '2':
            if not is_registered:
                response = "END You need to register first.\n"
                response += "Visit justlinkafrica.com to sign up.\n"
                response += "Then dial back for legal help."
            else:
                response = "CON Select issue category:\n"
                response += "1. Labour dispute\n"
                response += "2. Land dispute\n"
                response += "3. Family law\n"
                response += "4. Domestic violence\n"
                response += "5. Police abuse\n"
                response += "6. Other"

        elif text == '2*1':
            if is_registered:
                # create a pending case for them
                LegalCase.objects.create(
                    user=user,
                    issue_category='labour dispute',
                    description='Case submitted via USSD',
                    status='pending',
                    channel='USSD'
                )
                response = "END Your labour dispute case\n"
                response += "has been logged.\n"
                response += "A lawyer will contact you\n"
                response += f"on {phone_number} within 24hrs."
            else:
                response = "END Please register first at\n"
                response += "justlinkafrica.com"

        elif text == '3':
            response = "END To browse lawyers visit:\n"
            response += "justlinkafrica.com/lawyers\n"
            response += "Filter by country and specialization."

        elif text == '4':
            response = "END JustLink Africa connects\n"
            response += "individuals with lawyers and NGOs.\n"
            response += "Free legal first aid for all.\n"
            response += "justlinkafrica.com"

        else:
            response = "END Invalid option.\n"
            response += "Please dial again."

        return HttpResponse(response, content_type='text/plain')
